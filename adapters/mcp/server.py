"""Infraestructura compartida de los adapters MCP.

La instancia de FastMCP y la proyección de las tools viven acá, no en el módulo de
un dominio: un tool de `pacientes` no debe colgar de un archivo llamado
`contabilidad.py`. Los módulos de dominio importan `mcp` de acá y registran encima
sus propias tools, que no tienen lógica: autorizan contra el contrato del registry,
delegan en el service y serializan (V2 R6).
"""

import json
from typing import Annotated

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from application.errors import DomainError
from application.registry import get_contract
from security import authorize_contract, identity_from_mcp

# Un solo servidor, una sola URL y un solo token para todos los dominios (arquitectura
# §3). El nombre es una etiqueta que ve el cliente: renombrarlo obligaría a tocar la
# config de cada cliente MCP sin ganar nada funcional.
mcp = FastMCP("control-contable", streamable_http_path="/")

# El schema MCP se deriva de la firma, así que la pista de formato viaja en el
# Annotated: sin esto el agente solo ve "fecha: string" sin saber que es YYYY-MM-DD.
FechaArg = Annotated[
    str, Field(description="Fecha obligatoria en formato YYYY-MM-DD.")
]
OrigenArg = Annotated[
    str | None,
    Field(
        default=None,
        description=(
            "Canal opcional: CAJA, TOTEM o WEBPAY. Si se omite, devuelve los tres canales."
        ),
    ),
]


def _contract(capability_id: str):
    return get_contract(capability_id)


def _tool(capability_id: str, title: str):
    """Construye ``annotations`` y ``description`` desde el contrato del registry."""
    c = _contract(capability_id)
    return {
        "name": c.mcp_name,
        "title": title,
        "description": c.mcp_description,
        "annotations": ToolAnnotations(title=c.title, **c.annotations),
    }


def _run(capability_id: str, ctx: Context, fn, *args):
    """Autoriza, ejecuta y traduce DomainError a error MCP legible.

    FastMCP plasma la excepción como isError=true con este mensaje, sin traceback.
    """
    authorize_contract(capability_id, identity_from_mcp(ctx))
    try:
        return fn(*args)
    except DomainError as exc:
        raise RuntimeError(f"[{exc.error_code}] {exc.message}") from exc


def _json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, default=str)
