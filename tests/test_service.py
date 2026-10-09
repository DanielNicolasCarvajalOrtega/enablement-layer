from datetime import date
from decimal import Decimal

import pytest

from application.contabilidad.models import ORIGENES
from application.contabilidad.ports import (
    BoletaPorUsuarioRow,
    ContabilidadPort,
    DeudaRow,
    IngresoRow,
    PrevisionRow,
    TarjetaRow,
)
from application.contabilidad.service import ContabilidadService
from application.errors import NotFoundError, ValidationError


class FakeRepo(ContabilidadPort):
    """Doble de prueba. Cada método devuelve lo que el test le configura."""

    def __init__(
        self,
        rows: list[IngresoRow] | None = None,
        deuda: dict[str, DeudaRow | None] | None = None,
        tarjeta: dict[str, list[TarjetaRow]] | None = None,
        prevision: list[PrevisionRow] | None = None,
        emitidas: list[BoletaPorUsuarioRow] | None = None,
        anuladas: list[BoletaPorUsuarioRow] | None = None,
    ):
        self.rows = rows or []
        self.deuda = deuda or {}
        self.tarjeta = tarjeta or {}
        self.prevision = prevision or []
        self.emitidas = emitidas or []
        self.anuladas = anuladas or []
        self.tarjeta_llamadas: list[tuple[date, str]] = []
        self.deuda_llamados: list[str] = []

    def ingresos_por_tipo_pago(self, fecha: date) -> list[IngresoRow]:
        return self.rows

    def deuda_del_mes(self, periodo: str) -> DeudaRow | None:
        self.deuda_llamados.append(periodo)
        return self.deuda.get(periodo)

    def ingresos_por_tipo_tarjeta(self, fecha: date, origen: str) -> list[TarjetaRow]:
        self.tarjeta_llamadas.append((fecha, origen))
        return self.tarjeta.get(origen, [])

    def ingresos_por_tipo_prevision(self, fecha: date) -> list[PrevisionRow]:
        return self.prevision

    def boletas_por_usuario(self, fecha: date) -> list[BoletaPorUsuarioRow]:
        return self.emitidas

    def boletas_anuladas_por_usuario(self, fecha: date) -> list[BoletaPorUsuarioRow]:
        return self.anuladas


def _service(**kwargs) -> ContabilidadService:
    return ContabilidadService(FakeRepo(**kwargs))


# --------------------------------------------------------------------------- #
# #2 · Q1 (sin cambios, se mantiene la cobertura existente)
# --------------------------------------------------------------------------- #


def test_mapea_tipos_y_total():
    svc = _service(rows=[
        IngresoRow("EFE", Decimal("1240000")),
        IngresoRow("TRJ", Decimal("980000")),
        IngresoRow("WEBPAY", Decimal("1650000")),
        IngresoRow("TOTEM", Decimal("730000")),
    ])
    out = svc.consultar_ingresos_por_tipo_pago(date(2026, 9, 25))

    assert len(out.items) == 4
    assert out.items[0].tipo_pago == "EFE"
    assert out.items[0].etiqueta == "CAJA - EFECTIVO"
    assert out.items[0].monto == Decimal("1240000")
    assert out.total == Decimal("4600000")


def test_en_orden_canonico():
    svc = _service(rows=[IngresoRow("TOTEM", Decimal("1")), IngresoRow("EFE", Decimal("2"))])
    out = svc.consultar_ingresos_por_tipo_pago(date(2026, 9, 25))
    assert [i.tipo_pago for i in out.items] == ["EFE", "TOTEM"]


def test_sin_datos_es_nodata():
    with pytest.raises(NotFoundError) as exc:
        _service(rows=[]).consultar_ingresos_por_tipo_pago(date(2026, 9, 25))
    assert exc.value.error_code == "NO_DATA"


def test_fecha_invalida_es_invalid_argument():
    with pytest.raises(ValidationError) as exc:
        _service().consultar_ingresos_por_tipo_pago("banana")
    assert exc.value.error_code == "INVALID_ARGUMENT"


def test_fecha_ausente_es_invalid_argument():
    with pytest.raises(ValidationError) as exc:
        _service().consultar_ingresos_por_tipo_pago(None)
    assert exc.value.error_code == "INVALID_ARGUMENT"


# --------------------------------------------------------------------------- #
# #1 · Q3 resumen de deuda
# --------------------------------------------------------------------------- #


def test_q3_consulta_4_periodos_descendentes_desde_el_mes_de_fecha():
    repo = FakeRepo(deuda={})
    svc = ContabilidadService(repo)
    with pytest.raises(NotFoundError):
        svc.consultar_resumen_deuda(date(2017, 12, 15))
    assert repo.deuda_llamados == ["2017-12", "2017-11", "2017-10", "2017-09"]


def test_q3_arma_etiqueta_y_periodo():
    svc = _service(deuda={
        "2017-12": DeudaRow("12", Decimal("900601075")),
        "2017-11": DeudaRow("11", Decimal("896653783")),
        "2017-10": DeudaRow("10", Decimal("891873367")),
        "2017-09": DeudaRow("09", Decimal("896509697")),
    })
    out = svc.consultar_resumen_deuda(date(2017, 12, 15))

    assert out.meses_consultados == 4
    assert [(i.mes, i.periodo) for i in out.items] == [
        ("12-2017", "2017-12"),
        ("11-2017", "2017-11"),
        ("10-2017", "2017-10"),
        ("09-2017", "2017-09"),
    ]
    assert out.items[0].deuda == Decimal("900601075")


def test_q3_omite_meses_sin_filas_no_los_pone_en_cero():
    # El legacy no agrega la fila del mes sin datos. Un cero sería mentira.
    svc = _service(deuda={
        "2017-12": DeudaRow("12", Decimal("900601075")),
        "2017-10": DeudaRow("10", Decimal("891873367")),
    })
    out = svc.consultar_resumen_deuda(date(2017, 12, 15))
    assert [i.periodo for i in out.items] == ["2017-12", "2017-10"]
    assert out.meses_consultados == 4


def test_q3_atraviesa_cambio_de_ano():
    repo = FakeRepo(deuda={"2018-01": DeudaRow("01", Decimal("500"))})
    svc = ContabilidadService(repo)
    svc.consultar_resumen_deuda(date(2018, 1, 10))
    assert repo.deuda_llamados == ["2018-01", "2017-12", "2017-11", "2017-10"]


def test_q3_salta_de_diciembre_a_enero():
    repo = FakeRepo(deuda={"2017-12": DeudaRow("12", Decimal("7"))})
    svc = ContabilidadService(repo)
    svc.consultar_resumen_deuda(date(2017, 12, 1))
    assert repo.deuda_llamados == ["2017-12", "2017-11", "2017-10", "2017-09"]


def test_q3_cuatro_meses_vacios_es_nodata():
    with pytest.raises(NotFoundError) as exc:
        _service(deuda={}).consultar_resumen_deuda(date(2013, 1, 1))
    assert exc.value.error_code == "NO_DATA"


def test_q3_fecha_invalida_es_invalid_argument():
    with pytest.raises(ValidationError) as exc:
        _service().consultar_resumen_deuda("banana")
    assert exc.value.error_code == "INVALID_ARGUMENT"


def test_q3_fecha_ausente_es_invalid_argument():
    with pytest.raises(ValidationError):
        _service().consultar_resumen_deuda(None)


# --------------------------------------------------------------------------- #
# #3 · Q10 ingresos por tipo de tarjeta
# --------------------------------------------------------------------------- #


def test_q10_sin_origen_consulta_los_tres_canales():
    repo = FakeRepo(tarjeta={
        "CAJA": [TarjetaRow("CRD1", "CRD1", 243, Decimal("15749600"))],
        "TOTEM": [TarjetaRow("CREDITO", "CRD1", 4, Decimal("92000"))],
        "WEBPAY": [TarjetaRow("DEBITO", "DEB1", 44, Decimal("1892500"))],
    })
    svc = ContabilidadService(repo)
    out = svc.consultar_ingresos_por_tipo_tarjeta(date(2025, 5, 12))

    assert [c for _, c in repo.tarjeta_llamadas] == list(ORIGENES)
    assert [t.origen for t in out.totales] == ["CAJA", "TOTEM", "WEBPAY"]
    assert out.total.cantidad == 243 + 4 + 44
    assert out.total.monto == Decimal("15749600") + Decimal("92000") + Decimal("1892500")


def test_q10_con_origen_consulta_solo_ese_canal():
    repo = FakeRepo(tarjeta={"CAJA": [TarjetaRow("CRD1", "CRD1", 2, Decimal("100"))]})
    svc = ContabilidadService(repo)
    out = svc.consultar_ingresos_por_tipo_tarjeta(date(2025, 5, 12), "CAJA")

    assert repo.tarjeta_llamadas == [(date(2025, 5, 12), "CAJA")]
    assert [t.origen for t in out.totales] == ["CAJA"]
    assert out.total.cantidad == 2


def test_q10_normaliza_tipo_tarjeta_entre_canales():
    # CAJA entrega el código crudo (el legacy no aplica decode ahí); TOTEM y WEBPAY
    # lo entregan ya decodificado. tipo_tarjeta debe quedar comparable.
    svc = _service(tarjeta={
        "CAJA": [TarjetaRow("CRD1", "CRD1", 243, Decimal("15749600"))],
        "TOTEM": [TarjetaRow("DEBITO", "DEB1", 7, Decimal("206500"))],
    })
    out = svc.consultar_ingresos_por_tipo_tarjeta(date(2025, 5, 12))

    por_canal = {i.origen: i for i in out.items}
    assert por_canal["CAJA"].tipo_tarjeta == "CREDITO"
    assert por_canal["TOTEM"].tipo_tarjeta == "DEBITO"
    # El crudo y la etiqueta del correo se conservan para poder diffear contra el mail.
    assert por_canal["CAJA"].codigo_tarjeta == "CRD1"
    assert por_canal["CAJA"].etiqueta_correo == "CRD1"
    assert por_canal["TOTEM"].codigo_tarjeta == "DEB1"
    assert por_canal["TOTEM"].etiqueta_correo == "DEBITO"


def test_q10_mantiene_codigos_no_mapeados():
    svc = _service(tarjeta={"CAJA": [TarjetaRow("XYZ", "XYZ", 1, Decimal("10"))]})
    out = svc.consultar_ingresos_por_tipo_tarjeta(date(2025, 5, 12), "CAJA")
    assert out.items[0].tipo_tarjeta == "XYZ"


def test_q10_calcula_totales_por_canal_y_gran_total():
    svc = _service(tarjeta={
        "CAJA": [
            TarjetaRow("CRD1", "CRD1", 243, Decimal("15749600")),
            TarjetaRow("DEB1", "DEB1", 843, Decimal("30033500")),
        ],
        "TOTEM": [TarjetaRow("DEBITO", "DEB1", 7, Decimal("206500"))],
    })
    out = svc.consultar_ingresos_por_tipo_tarjeta(date(2025, 5, 12))

    totales = {t.origen: t for t in out.totales}
    assert totales["CAJA"].cantidad == 1086
    assert totales["CAJA"].monto == Decimal("45783100")
    assert totales["TOTEM"].cantidad == 7
    assert totales["WEBPAY"].cantidad == 0
    assert totales["WEBPAY"].monto == Decimal("0.00")  # canal vacío, total en cero
    assert out.total.cantidad == 1093
    assert out.total.monto == Decimal("45989600")  # 45.783.100 CAJA + 206.500 TOTEM


def test_q10_ordena_por_codigo_dentro_del_canal():
    svc = _service(tarjeta={"CAJA": [
        TarjetaRow("DEB1", "DEB1", 843, Decimal("30033500")),
        TarjetaRow("CRD1", "CRD1", 243, Decimal("15749600")),
    ]})
    out = svc.consultar_ingresos_por_tipo_tarjeta(date(2025, 5, 12), "CAJA")
    assert [i.codigo_tarjeta for i in out.items] == ["CRD1", "DEB1"]


def test_q10_todos_los_canales_vacios_es_nodata():
    with pytest.raises(NotFoundError) as exc:
        _service(tarjeta={}).consultar_ingresos_por_tipo_tarjeta(date(2025, 5, 12))
    assert exc.value.error_code == "NO_DATA"


def test_q10_origen_invalido_es_invalid_argument():
    with pytest.raises(ValidationError) as exc:
        _service().consultar_ingresos_por_tipo_tarjeta(date(2025, 5, 12), "CAJITA")
    assert exc.value.error_code == "INVALID_ARGUMENT"


def test_q10_fecha_invalida_es_invalid_argument():
    with pytest.raises(ValidationError):
        _service().consultar_ingresos_por_tipo_tarjeta("banana")


# --------------------------------------------------------------------------- #
# #4 · Q11 ingresos por tipo de previsión
# --------------------------------------------------------------------------- #


def test_q11_mapea_filas_y_totales():
    svc = _service(prevision=[
        PrevisionRow("2022 BRACKET METALICO V2", 301, Decimal("7867000")),
        PrevisionRow("2024 BRACKET METALICO", 534, Decimal("28414500")),
    ])
    out = svc.consultar_ingresos_por_tipo_prevision(date(2025, 5, 12))

    assert [i.prevision for i in out.items] == [
        "2022 BRACKET METALICO V2",
        "2024 BRACKET METALICO",
    ]
    assert out.total_cantidad == 835
    assert out.total_monto == Decimal("36281500")


def test_q11_conserva_el_orden_del_sql():
    # El legacy ordena por DOMIDESCRI; la capa no reordena.
    svc = _service(prevision=[
        PrevisionRow("B", 1, Decimal("1")),
        PrevisionRow("A", 1, Decimal("1")),
    ])
    out = svc.consultar_ingresos_por_tipo_prevision(date(2025, 5, 12))
    assert [i.prevision for i in out.items] == ["B", "A"]


def test_q11_sin_datos_es_nodata():
    with pytest.raises(NotFoundError) as exc:
        _service(prevision=[]).consultar_ingresos_por_tipo_prevision(date(2025, 5, 12))
    assert exc.value.error_code == "NO_DATA"


def test_q11_fecha_invalida_es_invalid_argument():
    with pytest.raises(ValidationError):
        _service().consultar_ingresos_por_tipo_prevision("banana")


# --------------------------------------------------------------------------- #
# #5 · Q8 boletas emitidas por usuario
# --------------------------------------------------------------------------- #


def test_q8_mapea_usuario_y_totales():
    svc = _service(emitidas=[
        BoletaPorUsuarioRow("MENDEZ", "ROXANA IVETTE", 114, Decimal("2735000")),
        BoletaPorUsuarioRow("JOFRE", "VANIA", 98, Decimal("2595100")),
    ])
    out = svc.consultar_boletas_emitidas_por_usuario(date(2025, 5, 12))

    assert out.items[0].usuario == "JOFRE VANIA"  # ordenado por apellido
    assert out.total_cantidad == 212
    assert out.total_monto == Decimal("5330100")


def test_q8_orden_canonico_estable():
    # El legacy no ordena; la capa fija apellido + nombre para que el contrato sea estable.
    svc = _service(emitidas=[
        BoletaPorUsuarioRow("ZELADA", "KATHALINA", 1, Decimal("1")),
        BoletaPorUsuarioRow("MENDEZ", "ROXANA", 1, Decimal("1")),
        BoletaPorUsuarioRow("MENDEZ", "ANA", 1, Decimal("1")),
    ])
    out = svc.consultar_boletas_emitidas_por_usuario(date(2025, 5, 12))
    assert [i.usuario for i in out.items] == ["MENDEZ ANA", "MENDEZ ROXANA", "ZELADA KATHALINA"]


def test_q8_mantiene_el_usuario_sistema():
    # El legacy devuelve USUAPEP='.', USUNOMC='SISTEMA'; no es un error de datos.
    svc = _service(emitidas=[BoletaPorUsuarioRow(".", "SISTEMA", 28, Decimal("1785000"))])
    out = svc.consultar_boletas_emitidas_por_usuario(date(2026, 9, 30))
    assert out.items[0].usuario == ". SISTEMA"
    assert out.total_cantidad == 28


def test_q8_sin_datos_es_nodata():
    with pytest.raises(NotFoundError) as exc:
        _service(emitidas=[]).consultar_boletas_emitidas_por_usuario(date(2025, 5, 12))
    assert exc.value.error_code == "NO_DATA"


def test_q8_fecha_invalida_es_invalid_argument():
    with pytest.raises(ValidationError):
        _service().consultar_boletas_emitidas_por_usuario("banana")


# --------------------------------------------------------------------------- #
# #6 · Q9 boletas anuladas por usuario
# --------------------------------------------------------------------------- #


def test_q9_mapea_usuario_y_totales():
    svc = _service(anuladas=[
        BoletaPorUsuarioRow("MORALES", "VICENTE", 28, Decimal("3247000")),
        BoletaPorUsuarioRow("ZELADA", "KATHALINA ALEJANDRA", 17, Decimal("1181000")),
    ])
    out = svc.consultar_boletas_anuladas_por_usuario(date(2025, 5, 12))

    assert [i.usuario for i in out.items] == ["MORALES VICENTE", "ZELADA KATHALINA ALEJANDRA"]
    assert out.total_cantidad == 45
    assert out.total_monto == Decimal("4428000")


def test_q9_sin_datos_es_nodata():
    with pytest.raises(NotFoundError) as exc:
        _service(anuladas=[]).consultar_boletas_anuladas_por_usuario(date(2025, 5, 12))
    assert exc.value.error_code == "NO_DATA"


def test_q9_fecha_invalida_es_invalid_argument():
    with pytest.raises(ValidationError):
        _service().consultar_boletas_anuladas_por_usuario("banana")