#!/usr/bin/env python3
"""
Ollama (http://localhost:11434/v1) + uno o varios servidores MCP, con qwen2.5-coder:7b.

qwen2.5-coder NO emite tool_calls nativos en Ollama: devuelve texto. Por eso la
selección de herramienta se fuerza con structured outputs (json_schema) y la
ejecución la hace este script, nunca el LLM.

Soporta preguntas que requieren varias tools (loop agéntico acotado) y varios
servidores MCP, todos ellos expuestos también como API REST.
"""
import asyncio
import json
import os
import re
import sys

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Token del .env (AUTH_TOKEN_AI_AGENT)
BEARER_TOKEN = os.environ.get("AUTH_TOKEN_AI_AGENT", "")
OLLAMA_URL = "http://localhost:11434/v1/chat/completions"
MODEL = "qwen2.5-coder:7b"
MAX_TURNS = 4

MCP_SERVERS = [
    {"name": "contabilidad", "url": "http://127.0.0.1:8090/mcp"},
    # {"name": "otro-servicio", "url": "http://127.0.0.1:8091/mcp"},
]


async def _with_session(url, fn):
    """Abre una sesión MCP, ejecuta fn(session) y cierra."""
    async with streamablehttp_client(
        url, headers={"Authorization": f"Bearer {BEARER_TOKEN}"}
    ) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await fn(session)


async def discover_tools() -> dict[str, dict]:
    """Catálogo unificado de tools de todos los servidores MCP.

    Devuelve {tool_name: {"server", "description", "inputSchema"}}.
    Ante colisión de nombres entre servidores, el sufijo queda explícito.
    """
    catalogo: dict[str, dict] = {}
    for srv in MCP_SERVERS:
        async def _list(session, srv=srv):
            listing = await session.list_tools()
            return [(t.name, t.description or "", t.inputSchema or {}) for t in listing.tools]

        for name, description, schema in await _with_session(srv["url"], _list):
            exposed = name
            if exposed in catalogo:
                exposed = f"{srv['name']}__{name}"
            catalogo[exposed] = {
                "server": srv,
                "tool": name,
                "description": description.strip(),
                "inputSchema": schema,
            }
    return catalogo


def build_decision_prompt(catalogo: dict[str, dict], pregunta: str, resultados: list) -> str:
    lineas = []
    for name, meta in catalogo.items():
        props = meta["inputSchema"].get("properties", {})
        requerido = meta["inputSchema"].get("required", [])
        params = ", ".join(
            f"{k}{'*' if k in requerido else ''}: {v.get('type', '?')}" for k, v in props.items()
        )
        resumen = (meta["description"].splitlines() or ["(sin descripción)"])[0]
        lineas.append(f"- {name}  [servidor: {meta['server']['name']}]\n    {resumen}\n    params: {params}")

    contexto = ""
    if resultados:
        previo = "\n".join(
            f"  · {r['tool']}({json.dumps(r['arguments'], ensure_ascii=False)}) -> "
            f"{json.dumps(r['data'], ensure_ascii=False)[:400]}"
            for r in resultados
        )
        contexto = f"\nDatos ya obtenidos:\n{previo}\n"

    return (
        "Eres un planificador que decide el siguiente paso para responder una pregunta "
        "usando herramientas de consulta.\n\n"
        f"Herramientas disponibles:\n" + "\n".join(lineas) + "\n"
        f"{contexto}\n"
        f"Pregunta: {pregunta}\n\n"
        "Elige UNA sola herramienta para el siguiente paso. Reglas:\n"
        "- Si los datos ya obtenidos responden completamente la pregunta, usa 'ninguno'.\n"
        "- Si falta información, elige la herramienta que la aporte.\n"
        "- Si necesitas más de un paso, elige solo el primero; se te volverá a preguntar.\n"
        "- No inventes herramientas que no estén en la lista.\n\n"
        'Responde SOLO con el JSON. Usa "tool": "ninguno" si no hace falta consultar nada.'
    )


def build_pregunta(argv: list[str]) -> str:
    """Acepta una pregunta completa o una fecha suelta (YYYY-MM-DD)."""
    entrada = " ".join(argv).strip()
    if not entrada:
        return "¿Cuánto se recaudó el 2026-09-29 por tipo de pago?"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", entrada):
        return f"¿Cuánto se recaudó el {entrada} por tipo de pago?"
    return entrada


async def main():
    pregunta = build_pregunta(sys.argv[1:])

    catalogo = await discover_tools()
    print("🔧 Catálogo de tools MCP:")
    for name, meta in catalogo.items():
        print(f"   · {name}  ({meta['server']['name']})")
    print()

    decision_schema = {
        "type": "object",
        "properties": {
            "tool": {"type": "string", "enum": list(catalogo.keys()) + ["ninguno"]},
            "arguments": {"type": "object"},
            "reason": {"type": "string"},
        },
        "required": ["tool", "arguments", "reason"],
    }

    resultados: list[dict] = []
    vistos: set[str] = set()

    async with httpx.AsyncClient(timeout=300.0) as client:

        async def chat(messages: list, schema: dict | None = None) -> dict:
            payload = {
                "model": MODEL,
                "messages": messages,
                "temperature": 0,
                "stream": False,
                "options": {"keep_alive": "10m"},
            }
            if schema:
                payload["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {"name": "decision_tool", "schema": schema},
                }
            resp = await client.post(OLLAMA_URL, json=payload)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]

        print(f"🤖 Pregunta: {pregunta}\n")

        for turno in range(1, MAX_TURNS + 1):
            msg = await chat(
                [{"role": "user", "content": build_decision_prompt(catalogo, pregunta, resultados)}],
                decision_schema,
            )

            print("─" * 60)
            print(f"📤 Paso {turno} — respuesta cruda del LLM (nada ejecutado todavía):")
            print(msg["content"])
            print("─" * 60)

            decision = json.loads(msg["content"])
            tool_name = decision.get("tool")
            tool_args = decision.get("arguments", {}) or {}
            print(f"🧠 Razón: {decision.get('reason', '(sin razón)')}")

            if tool_name == "ninguno":
                print("✅ El LLM considera que los datos obtenidos bastan.")
                break

            if tool_name not in catalogo:
                print(f"⛔ Tool '{tool_name}' no existe. Válidas: {sorted(catalogo)}")
                break

            firma = f"{tool_name}:{json.dumps(tool_args, sort_keys=True, ensure_ascii=False)}"
            if firma in vistos:
                print(f"🔁 Llamada repetida {firma}, corto para no ciclar.")
                break
            vistos.add(firma)

            meta = catalogo[tool_name]
            confirm = await asyncio.to_thread(
                input,
                f"\n🔧 Pedido: {tool_name}({json.dumps(tool_args, ensure_ascii=False)}) "
                f"→ servidor {meta['server']['name']}\n¿Ejecutar? [s/N] ",
            )
            if confirm.strip().lower() not in ("s", "si", "sí", "y"):
                print("✋ Cancelado. No se ejecutó la tool.")
                break

            async def _call(session, meta=meta, tool_args=tool_args):
                res = await session.call_tool(meta["tool"], tool_args)
                if res.isError:
                    raise RuntimeError(res.content[0].text if res.content else "error MCP")
                return json.loads(res.content[0].text) if res.content else {}

            try:
                data = await _with_session(meta["server"]["url"], _call)
            except Exception as exc:
                print(f"💥 Falló la tool: {exc}")
                break

            print(f"📥 Resultado:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
            resultados.append({"tool": tool_name, "arguments": tool_args, "data": data})
        else:
            print(f"⚠️  Se alcanzó el máximo de {MAX_TURNS} pasos.")

        if not resultados:
            msg = await chat([{"role": "user", "content": pregunta}])
            print(f"\n💬 Respuesta sin datos:\n{msg['content']}")
            return

        datos = "\n".join(
            f"{r['tool']}({json.dumps(r['arguments'], ensure_ascii=False)}) -> "
            f"{json.dumps(r['data'], ensure_ascii=False)}"
            for r in resultados
        )
        final_prompt = (
            f"Datos obtenidos:\n{datos}\n\n"
            f"Pregunta: {pregunta}\n\n"
            "Reglas:\n"
            "- Transcribe los montos dígito a dígito, sin agregar, quitar ni reordenar cifras.\n"
            "- Si un monto viene como string, respétalo tal cual.\n"
            "- No calcules ni inventes cifras que no estén en los datos.\n"
            "- Responde en español, breve y en lenguaje natural para un gerente de finanzas."
        )
        msg = await chat([{"role": "user", "content": final_prompt}])
        print(f"\n💬 Respuesta final de Ollama:\n{msg['content']}")


if __name__ == "__main__":
    asyncio.run(main())
