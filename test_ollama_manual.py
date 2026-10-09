#!/usr/bin/env python3
"""
Patrón manual: Tu código controla el flujo, LLM solo genera respuesta final
Funciona con qwen2.5-coder:7b sin function calling nativo
"""
import asyncio
import os
import sys
import httpx
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

# Token del .env (AUTH_TOKEN_AI_AGENT)
BEARER_TOKEN = os.environ.get("AUTH_TOKEN_AI_AGENT", "")
MCP_URL = "http://127.0.0.1:8090/mcp"
OLLAMA_URL = "http://localhost:11434/v1/chat/completions"
MODEL = "qwen2.5-coder:7b"


async def call_mcp_tool(tool_name: str, args: dict) -> dict:
    async with streamablehttp_client(
        MCP_URL, headers={"Authorization": f"Bearer {BEARER_TOKEN}"}
    ) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, args)
            if result.content:
                return json.loads(result.content[0].text)
            return {}


async def ollama_generate(prompt: str) -> str:
    payload = {"model": MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0, "stream": False}
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(OLLAMA_URL, json=payload)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def main():
    fecha = sys.argv[1] if len(sys.argv) > 1 else "2026-09-29"
    
    print(f"🔧 Consultando MCP para {fecha}...")
    data = await call_mcp_tool("consultar_ingresos_por_tipo_pago", {"fecha": fecha})
    
    print(f"📊 Datos: {json.dumps(data, ensure_ascii=False)}")
    
    prompt = f"""Eres un asistente contable. Responde en español natural.
Fecha: {fecha}
Datos de ingresos por tipo de pago:
{json.dumps(data, ensure_ascii=False, indent=2)}

Genera un resumen ejecutivo para un gerente de finanzas."""
    
    print("\n🧠 Generando respuesta con Ollama...")
    respuesta = await ollama_generate(prompt)
    print(f"\n💬 Respuesta:\n{respuesta}")


if __name__ == "__main__":
    import json
    asyncio.run(main())