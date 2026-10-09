"""Adapter MCP del bloque Pacientes.

Misma regla que el bloque contable: la tool autoriza contra el contrato del
registry, delega en el service y serializa. Acá la particularidad es que la tool
**no declara argumentos**: el schema MCP sale vacío y eso es parte del contrato
(la consulta es un censo de la cartera, sin filtros).
"""

from mcp.server.fastmcp import Context

from adapters.mcp.server import _json, _run, _tool, mcp
from composition import pacientes_service

T_POR_CIUDAD = "pacientes.pacientes_por_ciudad_chile"


@mcp.tool(**_tool(T_POR_CIUDAD, "Pacientes por ciudad (Chile)"))
def consultar_pacientes_por_ciudad_chile(ctx: Context) -> str:
    """Pacientes con dirección vigente agrupados por ciudad, de mayor a menor."""
    out = _run(T_POR_CIUDAD, ctx, pacientes_service.consultar_pacientes_por_ciudad_chile)
    return _json(
        {
            "items": [
                {"ciudad": i.ciudad, "cantidad_pacientes": i.cantidad_pacientes}
                for i in out.items
            ],
            "total_pacientes": out.total_pacientes,
            "cantidad_ciudades": out.cantidad_ciudades,
            "base": out.base,
            "incluye_pacientes_no_activos": True,
        }
    )
