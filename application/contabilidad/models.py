from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

Origen = Literal["CAJA", "TOTEM", "WEBPAY"]

ORIGENES: tuple[Origen, ...] = ("CAJA", "TOTEM", "WEBPAY")


class ConsultarIngresosPorTipoPagoInput(BaseModel):
    fecha: date = Field(..., description="Fecha obligatoria (YYYY-MM-DD). Las queries del legacy la exigen.")


class IngresoPorTipoPagoItem(BaseModel):
    tipo_pago: str = Field(..., description="EFE | TRJ | CHQ | WEBPAY | CAJA VECINA BCO.EST. | TOTEM")
    etiqueta: str = Field(..., description="Etiqueta legible como aparece en el correo.")
    monto: Decimal


class ConsultarIngresosPorTipoPagoOutput(BaseModel):
    fecha: date
    items: list[IngresoPorTipoPagoItem]
    total: Decimal


# --------------------------------------------------------------------------- #
# #1 consultar_resumen_deuda (Q3)
# --------------------------------------------------------------------------- #


class ConsultarResumenDeudaInput(BaseModel):
    fecha: date = Field(
        ...,
        description=(
            "Fecha obligatoria (YYYY-MM-DD). Solo se usan su año y mes: la capability "
            "devuelve ese mes y los 3 anteriores."
        ),
    )


class ResumenDeudaItem(BaseModel):
    mes: str = Field(..., description="Etiqueta del correo, MM-YYYY (ej. '09-2017').")
    periodo: str = Field(..., description="Periodo normalizado YYYY-MM (ej. '2017-09').")
    deuda: Decimal = Field(
        ...,
        description="PROMEDIO DIARIO de deuda del mes (round(avg(bat_deuda),0)), no el saldo de cierre.",
    )


class ConsultarResumenDeudaOutput(BaseModel):
    fecha: date
    meses_consultados: int = Field(
        ..., description="Períodos que se consultan en Oracle: 4, fijo del legacy (aunque some no tengan datos)."
    )
    items: list[ResumenDeudaItem] = Field(
        ..., description="Meses con datos, del más reciente al más antiguo. Sin datos van omitidos, no en cero."
    )


# --------------------------------------------------------------------------- #
# #3 consultar_ingresos_por_tipo_tarjeta (Q10)
# --------------------------------------------------------------------------- #


class ConsultarIngresosPorTipoTarjetaInput(BaseModel):
    fecha: date = Field(..., description="Fecha obligatoria (YYYY-MM-DD).")
    origen: Origen | None = Field(
        None,
        description=(
            "Canal opcional: CAJA | TOTEM | WEBPAY. Si se omite, devuelve los tres canales."
        ),
    )


class IngresoPorTipoTarjetaItem(BaseModel):
    origen: Origen
    tipo_tarjeta: str = Field(
        ..., description="Tipo uniforme que ve el agente: CREDITO | DEBITO (o el código crudo si no está mapeado)."
    )
    codigo_tarjeta: str = Field(..., description="Valor crudo de TIP_TARJETA: CRD1 | DEB1 | ...")
    etiqueta_correo: str = Field(
        ...,
        description="Lo que el legacy muestra para ese canal: el código crudo en CAJA, el tipo decodificado en TOTEM/WEBPAY.",
    )
    cantidad: int
    monto: Decimal


class TotalesPorOrigen(BaseModel):
    origen: Origen
    cantidad: int
    monto: Decimal


class TotalesGenerales(BaseModel):
    """Gran total de los canales consultados. Sin `origen` a propósito: puede
    abarcar varios canales y forzar uno sería mentirle al agente."""

    cantidad: int
    monto: Decimal


class ConsultarIngresosPorTipoTarjetaOutput(BaseModel):
    fecha: date
    items: list[IngresoPorTipoTarjetaItem] = Field(
        ..., description="Filas de los canales con datos, agrupadas por canal. Canales vacíos van omitidos."
    )
    totales: list[TotalesPorOrigen] = Field(
        ..., description="Un total por cada canal consultado, en orden CAJA, TOTEM, WEBPAY. Incluye los vacíos en cero."
    )
    total: TotalesGenerales = Field(
        ..., description="Gran total de los canales consultados, calculado por la capa (no por el LLM)."
    )


# --------------------------------------------------------------------------- #
# #4 consultar_ingresos_por_tipo_prevision (Q11)
# --------------------------------------------------------------------------- #


class ConsultarIngresosPorTipoPrevisionInput(BaseModel):
    fecha: date = Field(..., description="Fecha obligatoria (YYYY-MM-DD).")


class IngresoPorTipoPrevisionItem(BaseModel):
    prevision: str = Field(..., description="DOMIDESCRI literal de la tabla TIPO_PREVISION.")
    cantidad: int
    monto: Decimal


class ConsultarIngresosPorTipoPrevisionOutput(BaseModel):
    fecha: date
    items: list[IngresoPorTipoPrevisionItem] = Field(
        ..., description="Filas ordenadas por prevision (orden del legacy: order by DOMIDESCRI)."
    )
    total_cantidad: int
    total_monto: Decimal


# --------------------------------------------------------------------------- #
# #5 / #6 boletas por usuario (Q8 / Q9)
# --------------------------------------------------------------------------- #


class ConsultarBoletasPorUsuarioInput(BaseModel):
    fecha: date = Field(..., description="Fecha obligatoria (YYYY-MM-DD).")


class BoletaPorUsuarioItem(BaseModel):
    apellido: str = Field(..., description="USUAPEP. '.' cuando la boleta la emitió un proceso automático.")
    nombre: str = Field(..., description="USUNOMC.")
    usuario: str = Field(..., description="'APELLIDO NOMBRE', como lo arma el correo.")
    cantidad: int
    monto: Decimal


class ConsultarBoletasPorUsuarioOutput(BaseModel):
    fecha: date
    items: list[BoletaPorUsuarioItem] = Field(
        ..., description="Filas ordenadas por apellido y nombre. El legacy no garantiza orden, este es canónico."
    )
    total_cantidad: int
    total_monto: Decimal