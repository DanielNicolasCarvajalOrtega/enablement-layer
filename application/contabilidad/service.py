from datetime import date
from decimal import Decimal

from pydantic import ValidationError as PydanticValidationError

from application.contabilidad.models import (
    ConsultarBoletasPorUsuarioInput,
    ConsultarBoletasPorUsuarioOutput,
    ConsultarIngresosPorTipoPagoInput,
    ConsultarIngresosPorTipoPagoOutput,
    ConsultarIngresosPorTipoPrevisionInput,
    ConsultarIngresosPorTipoPrevisionOutput,
    ConsultarIngresosPorTipoTarjetaInput,
    ConsultarIngresosPorTipoTarjetaOutput,
    ConsultarResumenDeudaInput,
    ConsultarResumenDeudaOutput,
    IngresoPorTipoPagoItem,
    IngresoPorTipoPrevisionItem,
    IngresoPorTipoTarjetaItem,
    ResumenDeudaItem,
    BoletaPorUsuarioItem,
    ORIGENES,
    TotalesGenerales,
    TotalesPorOrigen,
)
from application.contabilidad.ports import ContabilidadPort
from application.errors import NotFoundError, ValidationError

LABELS = {
    "EFE": "CAJA - EFECTIVO",
    "TRJ": "CAJA - TARJETA",
    "CHQ": "CAJA - CHEQUE",
    "WEBPAY": "WEBPAY",
    "CAJA VECINA BCO.EST.": "CAJA VECINA BCO.EST.",
    "TOTEM": "TOTEM",
}

# Orden canónico de las filas (el legacy no garantiza orden; se fija uno estable).
CANONICAL_ORDER = ["EFE", "TRJ", "CHQ", "WEBPAY", "CAJA VECINA BCO.EST.", "TOTEM"]

# Q3 · el legacy recorre 4 períodos (i = 1..4) arrancando en el mes de fechaCns.
MESES_CONSULTADOS = 4

# Q10 · decode de TIP_TARJETA que el legacy aplica en SQL para TOTEM/WEBPAY pero NO
# para CAJA. Acá se aplica a los tres canales para que tipo_tarjeta sea uniforme.
# El valor crudo sigue disponible en codigo_tarjeta y lo que muestra el legacy
# para cada canal queda en etiqueta_correo.
TARJETA_LABELS = {
    "CRD1": "CREDITO",
    "DEB1": "DEBITO",
}


def _dec(entrada_modelo, campo: str, mensaje: str, **kwargs):
    """Valida con Pydantic y traduce el fallo a INVALID_ARGUMENT de la capa."""
    try:
        return entrada_modelo(**kwargs)
    except PydanticValidationError as exc:
        raise ValidationError(mensaje) from exc


def _periodo_anterior(periodo: str) -> str:
    """Resta un mes a 'YYYY-MM' respetando el salto de año del legacy."""
    anio, mes = int(periodo[:4]), int(periodo[5:7])
    if mes == 1:
        return f"{anio - 1:04d}-12"
    return f"{anio:04d}-{mes - 1:02d}"


class ContabilidadService:
    def __init__(self, repo: ContabilidadPort):
        self.repo = repo

    # ------------------------------------------------------------------ #
    # #2 · Q1 ingresos por tipo de pago
    # ------------------------------------------------------------------ #

    def consultar_ingresos_por_tipo_pago(self, fecha) -> ConsultarIngresosPorTipoPagoOutput:
        try:
            entrada = ConsultarIngresosPorTipoPagoInput(fecha=fecha)
        except PydanticValidationError as exc:
            raise ValidationError("fecha es obligatoria y debe ser YYYY-MM-DD.") from exc
        rows = self.repo.ingresos_por_tipo_pago(entrada.fecha)
        items, total = self._armar(rows)
        if not items:
            raise NotFoundError("No hay boletas activas para esa fecha. Resultado válido, no es un fallo.")
        return ConsultarIngresosPorTipoPagoOutput(fecha=entrada.fecha, items=items, total=total)

    @staticmethod
    def _armar(rows):
        montos = {r.tipo_pago: r.monto for r in rows}
        items = []
        total = Decimal("0.00")
        for tipo in CANONICAL_ORDER:
            if tipo in montos:
                items.append(
                    IngresoPorTipoPagoItem(tipo_pago=tipo, etiqueta=LABELS[tipo], monto=montos[tipo])
                )
                total += montos[tipo]
        return items, total

    # ------------------------------------------------------------------ #
    # #1 · Q3 resumen de deuda
    # ------------------------------------------------------------------ #

    def consultar_resumen_deuda(self, fecha) -> ConsultarResumenDeudaOutput:
        entrada = _dec(
            ConsultarResumenDeudaInput,
            "fecha",
            "fecha es obligatoria y debe ser YYYY-MM-DD.",
            fecha=fecha,
        )

        # Se replica el loop del legacy (i = 1..4): se consulta el mes de fecha y
        # se retrocede mes a mes. No se colapsa a una query con RANGE: el legacy
        # hace 4 ejecuciones y esta capa mantiene la misma cantidad de viajes.
        periodos = []
        periodo = f"{entrada.fecha.year:04d}-{entrada.fecha.month:02d}"
        for _ in range(MESES_CONSULTADOS):
            periodos.append(periodo)
            periodo = _periodo_anterior(periodo)

        items = []
        for periodo in periodos:
            row = self.repo.deuda_del_mes(periodo)
            # Mes sin filas: el legacy no agrega la fila. Omitir, no poner en cero.
            if row is None:
                continue
            items.append(
                ResumenDeudaItem(
                    mes=f"{row.mes}-{periodo[:4]}",
                    periodo=periodo,
                    deuda=row.deuda,
                )
            )

        if not items:
            raise NotFoundError(
                f"Sin registros de deuda para {periodos[0]} ni los {MESES_CONSULTADOS - 1} meses previos. "
                "Resultado válido, no es un fallo."
            )

        return ConsultarResumenDeudaOutput(
            fecha=entrada.fecha,
            meses_consultados=MESES_CONSULTADOS,
            items=items,
        )

    # ------------------------------------------------------------------ #
    # #3 · Q10 ingresos por tipo de tarjeta
    # ------------------------------------------------------------------ #

    def consultar_ingresos_por_tipo_tarjeta(self, fecha, origen=None) -> ConsultarIngresosPorTipoTarjetaOutput:
        entrada = _dec(
            ConsultarIngresosPorTipoTarjetaInput,
            "origen",
            "fecha es obligatoria y debe ser YYYY-MM-DD; origen debe ser CAJA, TOTEM o WEBPAY.",
            fecha=fecha,
            origen=origen,
        )

        canales = (entrada.origen,) if entrada.origen else ORIGENES

        items: list[IngresoPorTipoTarjetaItem] = []
        totales: list[TotalesPorOrigen] = []
        gran_total_cantidad = 0
        gran_total_monto = Decimal("0.00")

        for canal in canales:
            rows = self.repo.ingresos_por_tipo_tarjeta(entrada.fecha, canal)
            subtotal_cantidad = 0
            subtotal_monto = Decimal("0.00")

            for row in sorted(rows, key=lambda r: r.codigo):
                # El SQL de CAJA entrega el código crudo y el de TOTEM/WEBPAY ya
                # decodificado. Se normaliza para que tipo_tarjeta sea comparable
                # entre canales; el crudo y la etiqueta del correo se conservan.
                codigo = row.codigo
                tipo_uniforme = TARJETA_LABELS.get(codigo, row.tipo)
                items.append(
                    IngresoPorTipoTarjetaItem(
                        origen=canal,
                        tipo_tarjeta=tipo_uniforme,
                        codigo_tarjeta=codigo,
                        etiqueta_correo=row.tipo,
                        cantidad=row.cantidad,
                        monto=row.monto,
                    )
                )
                subtotal_cantidad += row.cantidad
                subtotal_monto += row.monto

            totales.append(
                TotalesPorOrigen(
                    origen=canal, cantidad=subtotal_cantidad, monto=subtotal_monto
                )
            )
            gran_total_cantidad += subtotal_cantidad
            gran_total_monto += subtotal_monto

        if not items:
            raise NotFoundError(
                f"No hay boletas de tarjeta (TRJ) para {entrada.fecha} en los canales: "
                f"{', '.join(canales)}. Resultado válido, no es un fallo."
            )

        return ConsultarIngresosPorTipoTarjetaOutput(
            fecha=entrada.fecha,
            items=items,
            totales=totales,
            total=TotalesGenerales(cantidad=gran_total_cantidad, monto=gran_total_monto),
        )

    # ------------------------------------------------------------------ #
    # #4 · Q11 ingresos por tipo de previsión
    # ------------------------------------------------------------------ #

    def consultar_ingresos_por_tipo_prevision(self, fecha) -> ConsultarIngresosPorTipoPrevisionOutput:
        entrada = _dec(
            ConsultarIngresosPorTipoPrevisionInput,
            "fecha",
            "fecha es obligatoria y debe ser YYYY-MM-DD.",
            fecha=fecha,
        )
        rows = self.repo.ingresos_por_tipo_prevision(entrada.fecha)
        if not rows:
            raise NotFoundError(
                f"No hay boletas activas con previsión para {entrada.fecha}. "
                "Resultado válido, no es un fallo."
            )

        items = [
            IngresoPorTipoPrevisionItem(prevision=r.prevision, cantidad=r.cantidad, monto=r.monto)
            for r in rows
        ]
        return ConsultarIngresosPorTipoPrevisionOutput(
            fecha=entrada.fecha,
            items=items,
            total_cantidad=sum(i.cantidad for i in items),
            total_monto=sum((i.monto for i in items), Decimal("0.00")),
        )

    # ------------------------------------------------------------------ #
    # #5 y #6 · Q8 / Q9 boletas por usuario
    # ------------------------------------------------------------------ #

    def consultar_boletas_emitidas_por_usuario(self, fecha) -> ConsultarBoletasPorUsuarioOutput:
        entrada = _dec(
            ConsultarBoletasPorUsuarioInput,
            "fecha",
            "fecha es obligatoria y debe ser YYYY-MM-DD.",
            fecha=fecha,
        )
        rows = self.repo.boletas_por_usuario(entrada.fecha)
        return self._armar_boletas_por_usuario(entrada.fecha, rows, "boletas activas")

    def consultar_boletas_anuladas_por_usuario(self, fecha) -> ConsultarBoletasPorUsuarioOutput:
        entrada = _dec(
            ConsultarBoletasPorUsuarioInput,
            "fecha",
            "fecha es obligatoria y debe ser YYYY-MM-DD.",
            fecha=fecha,
        )
        rows = self.repo.boletas_anuladas_por_usuario(entrada.fecha)
        return self._armar_boletas_por_usuario(entrada.fecha, rows, "boletas anuladas, devueltas o no cobradas")

    def _armar_boletas_por_usuario(self, fecha, rows, que: str) -> ConsultarBoletasPorUsuarioOutput:
        if not rows:
            raise NotFoundError(
                f"No hay {que} para {fecha}. Resultado válido, no es un fallo."
            )

        # El legacy hace GROUP BY USUAPEP, USUNOMC sin ORDER BY: el orden es el
        # que Oracle decida. Se fija uno canónico para que el contrato sea estable.
        ordenados = sorted(rows, key=lambda r: (r.apellido, r.nombre))
        items = [
            BoletaPorUsuarioItem(
                apellido=r.apellido,
                nombre=r.nombre,
                usuario=f"{r.apellido} {r.nombre}",
                cantidad=r.cantidad,
                monto=r.monto,
            )
            for r in ordenados
        ]
        return ConsultarBoletasPorUsuarioOutput(
            fecha=fecha,
            items=items,
            total_cantidad=sum(i.cantidad for i in items),
            total_monto=sum((i.monto for i in items), Decimal("0.00")),
        )