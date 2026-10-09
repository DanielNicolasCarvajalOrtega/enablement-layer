#!/usr/bin/env python3
"""
Ejemplo completo: Ollama (qwen2.5-coder:7b) + MCP tool 'consultar_ingresos_por_tipo_pago'
Requiere: ollama pull qwen2.5-coder:7b
"""
import asyncio
import json
import os
import sys
import ollama
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

# Token del .env (AUTH_TOKEN_AI_AGENT)
BEARER_TOKEN = os.environ.get("AUTH_TOKEN_AI_AGENT", "")


MCP_URL = "http://127.0.0.1:8090/mcp"

# Definición del tool para Ollama
TOOLS = [{
    "type": "function",
    "function": {
        "name": "consultar_ingresos_por_tipo_pago",
        "description": "Consulta los ingresos del día agrupados por tipo de pago (efectivo, tarjeta, cheque, webpay, totem, caja vecina). Retorna monto por tipo y total del día.",
        "parameters": {
            "type": "object",
            "properties": {
                "fecha": {"type": "string", "format": "date", "description": "Fecha en formato YYYY-MM-DD"}
            },
            "required": ["fecha"]
        }
    }
}]


async def call_mcp_tool(tool_name: str, args: dict) -> dict:
    """Ejecuta un tool en el servidor MCP"""
    async with streamablehttp_client(
        MCP_URL,
        headers={"Authorization": f"Bearer {BEARER_TOKEN}"}
    ) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, args)
            # Extraer el JSON del resultado
            if result.content and len(result.content) > 0:
                text = result.content[0].text
                return json.loads(text)
            return {}


async def main():
    fecha = sys.argv[1] if len(sys.argv) > 1 else "2026-09-29"
    pregunta = f"¿Cuánto se recaudó el {fecha} por tipo de pago?"
    
    print(f"🤖 Pregunta: {pregunta}")
    print(f"🔧 Llamando a MCP tool 'consultar_ingresos_por_tipo_pago' con fecha={fecha}...\n")
    
    # 1. Llamar directamente al MCP (sin LLM)
    resultado = await call_mcp_tool("consultar_ingresos_por_tipo_pago", {"fecha": fecha})
    print("📊 Resultado directo del MCP:")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60)
    print("🧠 Ahora usando Ollama (qwen2.5-coder:7b) con function calling...\n")
    
    # 2. Usar Ollama con function calling
    response = ollama.chat(
        model="qwen2.5-coder:7b",
        messages=[{"role": "user", "content": pregunta}],
        tools=TOOLS,
        options={"temperature": 0}
    )
    
    # Ver si el modelo quiere llamar al tool
    if response.message.tool_calls:
        for tool_call in response.message.tool_calls:
            print(f"🔧 Ollama quiere llamar: {tool_call.function.name}")
            print(f"   Argumentos: {tool_call.function.arguments}")
            
            # Ejecutar el tool en MCP
            mcp_result = await call_mcp_tool(tool_call.function.name, tool_call.function.arguments)
            
            print(f"📥 Resultado MCP: {json.dumps(mcp_result, ensure_ascii=False)}")
            
            # Enviar resultado de vuelta a Ollama para que genere respuesta final
            final_response = ollama.chat(
                model="qwen2.5-coder:7b",
                messages=[
                    {"role": "user", "content": pregunta},
                    response.message,
                    {"role": "tool", "content": json.dumps(mcp_result), "name": tool_call.function.name}
                ],
                options={"temperature": 0}
            )
            print(f"\n💬 Respuesta final de Ollama:")
            print(final_response.message.content)
    else:
        print("⚠️  Ollama no llamó al tool, respuesta directa:")
        print(response.message.content)


if __name__ == "__main__":
    asyncio.run(main())