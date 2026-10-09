"""Adapter MCP del bloque Control Contable.

Cada tool es una función delgada: autoriza contra el contrato del registry, delega
en el service y serializa. No hay lógica de negocio ni SQL acá (V2 R6/R15).

El nombre, la descripción y las ``annotations`` de cada tool salen del Capability
Registry, así que no puede haber deriva entre el contrato publicado y el
implementado (R17).
"""

from mcp.server.fastmcp import Context

from adapters.mcp.server import FechaArg, OrigenArg, _json, _run, _tool, mcp
from composition import contabilidad_service

# --------------------------------------------------------------------------- #
# #2 · Q1 ingresos por tipo de pago
# --------------------------------------------------------------------------- #

T1 = "contabilidad.ingresos_por_tipo_pago"


@mcp.tool(**_tool(T1, "Ingresos del día por tipo de pago"))
def consultar_ingresos_por_tipo_pago(fecha: FechaArg, ctx: Context) -> str:
    """Ingresos del día por tipo de pago (Q1)."""
    out = _run(T1, ctx, contabilidad_service.consultar_ingresos_por_tipo_pago, fecha)
    return _json(
        {
            "fecha": out.fecha.isoformat(),
            "items": [
                {"tipo_pago": i.tipo_pago, "etiqueta": i.etiqueta, "monto": str(i.monto)}
                for i in out.items
            ],
            "total": str(out.total),
        }
    )


# --------------------------------------------------------------------------- #
# #1 · Q3 resumen de deuda
# --------------------------------------------------------------------------- #

T3 = "contabilidad.resumen_deuda"


@mcp.tool(**_tool(T3, "Resumen de deuda de los últimos 4 meses"))
def consultar_resumen_deuda(fecha: FechaArg, ctx: Context) -> str:
    """Deuda promedio mensual de los últimos 4 meses (Q3)."""
    out = _run(T3, ctx, contabilidad_service.consultar_resumen_deuda, fecha)
    return _json(
        {
            "fecha": out.fecha.isoformat(),
            "meses_consultados": out.meses_consultados,
            "items": [
                {
                    "mes": i.mes,
                    "periodo": i.periodo,
                    "deuda": str(i.deuda),
                    "deuda_es_promedio_diario": True,
                }
                for i in out.items
            ],
        }
    )


# --------------------------------------------------------------------------- #
# #3 · Q10 ingresos por tipo de tarjeta
# --------------------------------------------------------------------------- #

T10 = "contabilidad.ingresos_por_tipo_tarjeta"


@mcp.tool(**_tool(T10, "Ingresos del día por tipo de tarjeta, por canal"))
def consultar_ingresos_por_tipo_tarjeta(fecha: FechaArg, ctx: Context, origen: OrigenArg = None) -> str:
    """Ingresos con boleta TRJ por tipo de tarjeta y canal (Q10).

    origen es opcional: si se omite, devuelve CAJA, TOTEM y WEBPAY.
    """
    out = _run(T10, ctx, contabilidad_service.consultar_ingresos_por_tipo_tarjeta, fecha, origen)
    return _json(
        {
            "fecha": out.fecha.isoformat(),
            "items": [
                {
                    "origen": i.origen,
                    "tipo_tarjeta": i.tipo_tarjeta,
                    "codigo_tarjeta": i.codigo_tarjeta,
                    "etiqueta_correo": i.etiqueta_correo,
                    "cantidad": i.cantidad,
                    "monto": str(i.monto),
                }
                for i in out.items
            ],
            "totales": [
                {"origen": t.origen, "cantidad": t.cantidad, "monto": str(t.monto)}
                for t in out.totales
            ],
            "total": {"cantidad": out.total.cantidad, "monto": str(out.total.monto)},
        }
    )


# --------------------------------------------------------------------------- #
# #4 · Q11 ingresos por tipo de previsión
# --------------------------------------------------------------------------- #

T11 = "contabilidad.ingresos_por_tipo_prevision"


@mcp.tool(**_tool(T11, "Ingresos del día por tipo de previsión"))
def consultar_ingresos_por_tipo_prevision(fecha: FechaArg, ctx: Context) -> str:
    """Ingresos del día agrupados por previsión (Q11)."""
    out = _run(T11, ctx, contabilidad_service.consultar_ingresos_por_tipo_prevision, fecha)
    return _json(
        {
            "fecha": out.fecha.isoformat(),
            "items": [
                {"prevision": i.prevision, "cantidad": i.cantidad, "monto": str(i.monto)}
                for i in out.items
            ],
            "total_cantidad": out.total_cantidad,
            "total_monto": str(out.total_monto),
        }
    )


# --------------------------------------------------------------------------- #
# #5 · Q8 boletas emitidas por usuario
# --------------------------------------------------------------------------- #

T8 = "contabilidad.boletas_emitidas_por_usuario"


@mcp.tool(**_tool(T8, "Boletas emitidas por usuario"))
def consultar_boletas_emitidas_por_usuario(fecha: FechaArg, ctx: Context) -> str:
    """Boletas activas del día agrupadas por usuario responsable (Q8)."""
    out = _run(T8, ctx, contabilidad_service.consultar_boletas_emitidas_por_usuario, fecha)
    return _json(_boletas_payload(out))


# --------------------------------------------------------------------------- #
# #6 · Q9 boletas anuladas por usuario
# --------------------------------------------------------------------------- #

T9 = "contabilidad.boletas_anuladas_por_usuario"


@mcp.tool(**_tool(T9, "Boletas anuladas, devueltas y no cobradas por usuario"))
def consultar_boletas_anuladas_por_usuario(fecha: FechaArg, ctx: Context) -> str:
    """Boletas ANU/DEV/NCI del día agrupadas por usuario (Q9). Filtra FEC_BOL exacto."""
    out = _run(T9, ctx, contabilidad_service.consultar_boletas_anuladas_por_usuario, fecha)
    return _json(_boletas_payload(out))


def _boletas_payload(out) -> dict:
    return {
        "fecha": out.fecha.isoformat(),
        "items": [
            {
                "apellido": i.apellido,
                "nombre": i.nombre,
                "usuario": i.usuario,
                "cantidad": i.cantidad,
                "monto": str(i.monto),
            }
            for i in out.items
        ],
        "total_cantidad": out.total_cantidad,
        "total_monto": str(out.total_monto),
    }