from datetime import date

from fastapi import APIRouter, Depends, Query

from application.contabilidad.models import (
    ConsultarBoletasPorUsuarioOutput,
    ConsultarIngresosPorTipoPagoOutput,
    ConsultarIngresosPorTipoPrevisionOutput,
    ConsultarIngresosPorTipoTarjetaOutput,
    ConsultarResumenDeudaOutput,
)
from application.registry import get_contract
from composition import contabilidad_service
from security import require_contract

router = APIRouter(prefix="/api/contabilidad", tags=["contabilidad"])


@router.get(
    "/ingresos-por-tipo-pago",
    response_model=ConsultarIngresosPorTipoPagoOutput,
    summary="Ingresos del día por tipo de pago",
)
def consultar_ingresos_por_tipo_pago(
    fecha: date = Query(..., description="Fecha obligatoria (YYYY-MM-DD)."),
    identity: dict = Depends(require_contract("contabilidad.ingresos_por_tipo_pago")),
):
    """Reproduce la tabla 'Ingresos por tipo pago' del correo de control contable (Q1)."""
    return contabilidad_service.consultar_ingresos_por_tipo_pago(fecha)


@router.get(
    "/resumen-deuda",
    response_model=ConsultarResumenDeudaOutput,
    summary="Resumen de deuda de los últimos 4 meses",
)
def consultar_resumen_deuda(
    fecha: date = Query(
        ...,
        description=(
            "Fecha obligatoria (YYYY-MM-DD). Solo se usan año y mes: devuelve ese mes "
            "y los 3 anteriores."
        ),
    ),
    identity: dict = Depends(require_contract("contabilidad.resumen_deuda")),
):
    """Reproduce la tabla 'Deuda promedio' del correo de control contable (Q3).

    Promedio diario de deuda por mes, no saldo de cierre.
    """
    return contabilidad_service.consultar_resumen_deuda(fecha)


@router.get(
    "/ingresos-por-tipo-tarjeta",
    response_model=ConsultarIngresosPorTipoTarjetaOutput,
    summary="Ingresos del día por tipo de tarjeta, por canal",
)
def consultar_ingresos_por_tipo_tarjeta(
    fecha: date = Query(..., description="Fecha obligatoria (YYYY-MM-DD)."),
    origen: str | None = Query(
        None,
        description="Canal opcional: CAJA | TOTEM | WEBPAY. Si se omite, devuelve los tres.",
    ),
    identity: dict = Depends(require_contract("contabilidad.ingresos_por_tipo_tarjeta")),
):
    """Reproduce las tres tablas de tarjeta del correo de control contable (Q10)."""
    return contabilidad_service.consultar_ingresos_por_tipo_tarjeta(fecha, origen)


@router.get(
    "/ingresos-por-tipo-prevision",
    response_model=ConsultarIngresosPorTipoPrevisionOutput,
    summary="Ingresos del día por tipo de previsión",
)
def consultar_ingresos_por_tipo_prevision(
    fecha: date = Query(..., description="Fecha obligatoria (YYYY-MM-DD)."),
    identity: dict = Depends(require_contract("contabilidad.ingresos_por_tipo_prevision")),
):
    """Reproduce la tabla 'Ingresos por tipo previsión' del correo (Q11)."""
    return contabilidad_service.consultar_ingresos_por_tipo_prevision(fecha)


@router.get(
    "/boletas-emitidas-por-usuario",
    response_model=ConsultarBoletasPorUsuarioOutput,
    summary="Boletas emitidas por usuario",
)
def consultar_boletas_emitidas_por_usuario(
    fecha: date = Query(..., description="Fecha obligatoria (YYYY-MM-DD)."),
    identity: dict = Depends(require_contract("contabilidad.boletas_emitidas_por_usuario")),
):
    """Reproduce la tabla 'Boletas por usuario' del correo de control contable (Q8)."""
    return contabilidad_service.consultar_boletas_emitidas_por_usuario(fecha)


@router.get(
    "/boletas-anuladas-por-usuario",
    response_model=ConsultarBoletasPorUsuarioOutput,
    summary="Boletas anuladas, devueltas y no cobradas por usuario",
)
def consultar_boletas_anuladas_por_usuario(
    fecha: date = Query(..., description="Fecha obligatoria (YYYY-MM-DD)."),
    identity: dict = Depends(require_contract("contabilidad.boletas_anuladas_por_usuario")),
):
    """Reproduce la tabla 'Boletas anuladas' del correo de control contable (Q9).

    Filtra por FEC_BOL exacto (sin trunc), igual que el legacy.
    """
    return contabilidad_service.consultar_boletas_anuladas_por_usuario(fecha)