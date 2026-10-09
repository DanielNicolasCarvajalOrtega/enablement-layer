#!/usr/bin/env python3
"""
Script básico para probar el MCP tool 'consultar_ingresos_por_tipo_pago'
usando Ollama + qwen2.5-coder:7b
"""
import asyncio
import json
import os
import sys
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Token del .env (AUTH_TOKEN_AI_AGENT)
BEARER_TOKEN = os.environ.get("AUTH_TOKEN_AI_AGENT", "")


async def main():
    fecha = sys.argv[1] if len(sys.argv) > 1 else "2026-09-29"
    
    # Conectar al servidor MCP vía streamable-http con autenticación
    async with streamablehttp_client(
        "http://127.0.0.1:8090/mcp",
        headers={"Authorization": f"Bearer {BEARER_TOKEN}"}
    ) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Listar tools disponibles
            tools = await session.list_tools()
            print("Tools disponibles:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Llamar al tool consultar_ingresos_por_tipo_pago
            print(f"\nConsultando ingresos por tipo de pago para {fecha}...")
            result = await session.call_tool(
                "consultar_ingresos_por_tipo_pago",
                {"fecha": fecha}
            )
            
            print("\nResultado:")
            print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())