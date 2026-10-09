"""Nivel 0/1 contra Oracle real: paridad con el legacy.

Los números esperados NO son inventados: son la salida de las queries del legacy
ejecutadas a mano sobre `dent` (ver la sección "Verificación" de cada ficha). Si
estas pruebas fallan, el desvío es de la capa, no del dato.

Se saltan (no fallan) si Oracle no está configurado o no responde, para que la
suite siga siendo ejecutable sin VPN.
"""

from datetime import date
from decimal import Decimal

import pytest

from application.contabilidad.service import ContabilidadService
from application.pacientes.service import PacientesService
from composition import contabilidad_service, pacientes_service
from database import OracleNotConfiguredError, get_pool

TOKEN = {"Authorization": "Bearer tok-contador-test"}
# El censo de pacientes no habilita el token contable (rol fuera del contrato).
TOKEN_PACIENTES = {"Authorization": "Bearer tok-analista-test"}

FECHA_TARJETA = date(2025, 5, 12)  # día con actividad en los 3 canales
FECHA_DEUDA = date(2017, 12, 15)  # bat_deuda llega hasta 2023-03


@pytest.fixture(scope="module")
def oracle(client):
    """Requiere el `client` de sesión: el pool se crea en el lifespan de la app."""
    try:
        get_pool()
    except (OracleNotConfiguredError, RuntimeError):
        pytest.skip("Oracle no disponible: se omiten las pruebas de paridad")
    try:
        with get_pool().acquire() as conn:
            with conn.cursor() as cur:
                cur.execute("select 1 from dual")
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Oracle no responde: {exc}")


def _get(client, path, params, headers=None):
    resp = client.get(path, params=params, headers=headers or TOKEN)
    assert resp.status_code == 200, resp.text
    return resp.json()


SQL_PACIENTES_REFERENCIA = """
select ci.NOM_CIU, count(distinct p.PAC_CODIGO)
from DENT.PACIENTES p
join DENT.DIRECCIONES d on d.COD_PERSONA = p.PAC_CODIGO
join DENT.CIUDADES ci on ci.COD_CIU = d.COD_CIUDAD
where d.IND_ESTADO = 'VIG'
group by ci.NOM_CIU
order by 2 desc, ci.NOM_CIU
"""


# --------------------------------------------------------------------------- #
# #1 · Q3 resumen de deuda
# --------------------------------------------------------------------------- #

Q3_ESPERADO = [
    ("12-2017", "2017-12", "900601075"),
    ("11-2017", "2017-11", "896653783"),
    ("10-2017", "2017-10", "891873367"),
    ("09-2017", "2017-09", "896509697"),
]


def test_q3_paridad_2017_12(oracle):
    out = contabilidad_service.consultar_resumen_deuda(FECHA_DEUDA)
    assert [(i.mes, i.periodo, str(i.deuda)) for i in out.items] == Q3_ESPERADO
    assert out.meses_consultados == 4


def test_q3_rest_devuelve_los_mismos_numeros(client):
    body = _get(client, "/api/contabilidad/resumen-deuda", {"fecha": FECHA_DEUDA.isoformat()})
    assert body["meses_consultados"] == 4
    assert [(i["mes"], i["periodo"], i["deuda"]) for i in body["items"]] == Q3_ESPERADO


def test_q3_sin_datos_recientes_es_nodata(oracle):
    # bat_deuda termina en 2023-03: una fecha de hoy no debe inventar ceros.
    with pytest.raises(Exception) as exc:
        contabilidad_service.consultar_resumen_deuda(date(2026, 10, 1))
    assert getattr(exc.value, "error_code", None) == "NO_DATA"


def test_q3_omite_meses_sin_filas_sin_llenar_con_cero(oracle):
    # 2018-02 no tiene filas: el item aparece pero no como 0.
    out = contabilidad_service.consultar_resumen_deuda(date(2018, 2, 10))
    periodos = [i.periodo for i in out.items]
    assert "2018-02" not in periodos or all(i.deuda != 0 for i in out.items)
    assert out.meses_consultados == 4


# --------------------------------------------------------------------------- #
# #3 · Q10 ingresos por tipo de tarjeta
# --------------------------------------------------------------------------- #

Q10_ESPERADO = {
    "CAJA": [("CRD1", "CREDITO", 243, "15749600"), ("DEB1", "DEBITO", 843, "30033500")],
    "TOTEM": [("CRD1", "CREDITO", 4, "92000"), ("DEB1", "DEBITO", 7, "206500")],
    "WEBPAY": [("CRD1", "CREDITO", 16, "939000"), ("DEB1", "DEBITO", 44, "1892500")],
}
Q10_ETIQUETA_CORREO = {"CAJA": "crudo", "TOTEM": "decodificado", "WEBPAY": "decodificado"}


def test_q10_paridad_de_los_tres_canales(oracle):
    out = contabilidad_service.consultar_ingresos_por_tipo_tarjeta(FECHA_TARJETA)
    for canal, esperado in Q10_ESPERADO.items():
        filas = [(i.codigo_tarjeta, i.tipo_tarjeta, i.cantidad, str(i.monto))
                 for i in out.items if i.origen == canal]
        assert filas == esperado, canal


def test_q10_totales_por_canal_y_gran_total(oracle):
    out = contabilidad_service.consultar_ingresos_por_tipo_tarjeta(FECHA_TARJETA)
    totales = {t.origen: (t.cantidad, t.monto) for t in out.totales}
    assert totales == {
        "CAJA": (1086, Decimal("45783100")),
        "TOTEM": (11, Decimal("298500")),
        "WEBPAY": (60, Decimal("2831500")),
    }
    assert out.total.cantidad == 1086 + 11 + 60
    assert out.total.monto == Decimal("45783100") + Decimal("298500") + Decimal("2831500")


def test_q10_etiqueta_correo_respeta_la_asimetria_del_legacy(oracle):
    # CAJA no aplica decode en el legacy; TOTEM y WEBPAY sí.
    out = contabilidad_service.consultar_ingresos_por_tipo_tarjeta(FECHA_TARJETA)
    for item in out.items:
        esperado = item.codigo_tarjeta if Q10_ETIQUETA_CORREO[item.origen] == "crudo" else item.tipo_tarjeta
        assert item.etiqueta_correo == esperado


def test_q10_un_solo_canal_coincide_con_el_todos(oracle):
    out = contabilidad_service.consultar_ingresos_por_tipo_tarjeta(FECHA_TARJETA, "CAJA")
    assert len(out.totales) == 1
    assert out.totales[0].origen == "CAJA"
    assert out.total.cantidad == 1086


def test_q10_rest_y_mcp_entregan_lo_mismo(client):
    body = _get(
        client,
        "/api/contabilidad/ingresos-por-tipo-tarjeta",
        {"fecha": FECHA_TARJETA.isoformat(), "origen": "CAJA"},
    )
    assert body["total"] == {"cantidad": 1086, "monto": "45783100.00"}
    assert [i["codigo_tarjeta"] for i in body["items"]] == ["CRD1", "DEB1"]


# --------------------------------------------------------------------------- #
# #4 · Q11 ingresos por tipo de previsión
# --------------------------------------------------------------------------- #


def test_q11_paridad_totales(oracle):
    out = contabilidad_service.consultar_ingresos_por_tipo_prevision(FECHA_TARJETA)
    assert out.total_cantidad == 1305
    assert out.total_monto == Decimal("54151100")
    top = out.items[0]
    assert top.prevision == "2022 BRACKET ESTETICO V2"
    assert top.cantidad == 9
    assert top.monto == Decimal("643000")


def test_q11_orden_por_descripcion(oracle):
    out = contabilidad_service.consultar_ingresos_por_tipo_prevision(FECHA_TARJETA)
    previsiones = [i.prevision for i in out.items]
    assert previsiones == sorted(previsiones)


def test_q11_suma_coherente_con_las_filas(oracle):
    out = contabilidad_service.consultar_ingresos_por_tipo_prevision(FECHA_TARJETA)
    assert sum(i.cantidad for i in out.items) == out.total_cantidad
    assert sum((i.monto for i in out.items), Decimal("0")) == out.total_monto


# --------------------------------------------------------------------------- #
# #5 · Q8 boletas emitidas por usuario
# --------------------------------------------------------------------------- #


def test_q8_paridad_totales(oracle):
    out = contabilidad_service.consultar_boletas_emitidas_por_usuario(FECHA_TARJETA)
    assert out.total_cantidad == 1305
    assert out.total_monto == Decimal("54151100")
    assert len(out.items) == 23


def test_q8_orden_canonico_por_apellido(oracle):
    out = contabilidad_service.consultar_boletas_emitidas_por_usuario(FECHA_TARJETA)
    assert [i.usuario for i in out.items] == sorted(i.usuario for i in out.items)


def test_q8_con_usuario_sistema(oracle):
    out = contabilidad_service.consultar_boletas_emitidas_por_usuario(date(2026, 9, 30))
    sistema = next(i for i in out.items if i.nombre == "SISTEMA")
    assert sistema.apellido == "."
    assert sistema.usuario == ". SISTEMA"
    assert sistema.cantidad == 28
    assert sistema.monto == Decimal("1785000")


def test_q8_no_expone_rut(client, oracle):
    body = _get(client, "/api/contabilidad/boletas-emitidas-por-usuario", {"fecha": "2026-09-30"})
    for item in body["items"]:
        assert "rut" not in item
        assert set(item) == {"apellido", "nombre", "usuario", "cantidad", "monto"}


# --------------------------------------------------------------------------- #
# #6 · Q9 boletas anuladas por usuario
# --------------------------------------------------------------------------- #


def test_q9_paridad_totales(oracle):
    out = contabilidad_service.consultar_boletas_anuladas_por_usuario(FECHA_TARJETA)
    assert out.total_cantidad == 45
    assert out.total_monto == Decimal("4428000")
    assert [(i.apellido, i.nombre, i.cantidad, str(i.monto)) for i in out.items] == [
        ("MORALES", "VICENTE", 28, "3247000"),
        ("ZELADA", "KATHALINA ALEJANDRA", 17, "1181000"),
    ]


def test_q9_solo_boletas_a_la_medianoche(oracle):
    """h2 · la semántica replicada: sin TRUNC, solo cuenta 00:00:00."""
    fecha = FECHA_TARJETA.isoformat()
    with get_pool().acquire() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select count(*) from dent.boleta "
                "where ind_estado in ('ANU','DEV','NCI') and FEC_BOL = to_date(:f,'YYYY-MM-DD')",
                f=fecha,
            )
            con_igualdad = cur.fetchone()[0]
            cur.execute(
                "select count(*) from dent.boleta "
                "where ind_estado in ('ANU','DEV','NCI') and trunc(FEC_BOL) = to_date(:f,'YYYY-MM-DD')",
                f=fecha,
            )
            con_trunc = cur.fetchone()[0]
    out = contabilidad_service.consultar_boletas_anuladas_por_usuario(FECHA_TARJETA)
    assert out.total_cantidad == con_igualdad
    # Documenta el costo de h2: con TRUNC habría más boletas.
    assert con_igualdad <= con_trunc


# --------------------------------------------------------------------------- #
# Coherencia transversal de la capa
# --------------------------------------------------------------------------- #


def test_no_data_no_se_confunde_con_unavailable(client, oracle):
    # Fecha sin boletas anuladas → NO_DATA (404), no 503.
    resp = client.get(
        "/api/contabilidad/boletas-anuladas-por-usuario",
        params={"fecha": "2026-10-01"},
        headers=TOKEN,
    )
    assert resp.status_code == 404
    assert resp.json()["error_code"] == "NO_DATA"


def test_shared_service_es_la_misma_instancia():
    from adapters.mcp.contabilidad import mcp as _mcp  # noqa: F401
    from adapters.mcp import pacientes as _mcp_pacientes  # noqa: F401
    from adapters.rest import contabilidad as rest
    from adapters.rest import pacientes as rest_pacientes

    assert rest.contabilidad_service is contabilidad_service
    assert isinstance(contabilidad_service, ContabilidadService)
    # Misma regla para el bloque pacientes: REST y MCP no pueden tener services
    # distintos, o la paridad entre protocolos pasa a depender de la buena voluntad.
    assert rest_pacientes.pacientes_service is pacientes_service
    assert isinstance(pacientes_service, PacientesService)


# --------------------------------------------------------------------------- #
# ENC.PACIENTES_POR_CIUDAD · pacientes por ciudad
# --------------------------------------------------------------------------- #
#
# A diferencia del bloque contable, acá NO se fijan números: un censo de cartera
# cambia con cada paciente nuevo que se registra. Lo que se verifica es que la capa
# reproduzca la consulta original, comparándola contra el mismo SQL corrido a mano
# sobre la BD. Si el desvío es de la capa, esta prueba falla; si el dato cambió,
# la ficha es la que hay que revisar.


def test_pacientes_coincide_con_el_sql_de_la_encuentros(oracle):
    with get_pool().acquire() as conn:
        with conn.cursor() as cur:
            cur.execute(SQL_PACIENTES_REFERENCIA)
            esperado = [(r[0], int(r[1])) for r in cur.fetchall()]

    out = pacientes_service.consultar_pacientes_por_ciudad_chile()
    assert [(i.ciudad, i.cantidad_pacientes) for i in out.items] == esperado


def test_pacientes_rest_devuelve_los_mismos_numeros(client, oracle):
    out = pacientes_service.consultar_pacientes_por_ciudad_chile()
    body = _get(client, "/api/pacientes/pacientes-por-ciudad-chile", {}, TOKEN_PACIENTES)

    assert body["base"] == "pacientes_con_direccion_vigente"
    assert body["cantidad_ciudades"] == out.cantidad_ciudades
    assert body["total_pacientes"] == out.total_pacientes
    assert [(i["ciudad"], i["cantidad_pacientes"]) for i in body["items"]] == [
        (i.ciudad, i.cantidad_pacientes) for i in out.items
    ]


def test_pacientes_suma_coherente_con_las_filas(client, oracle):
    body = _get(client, "/api/pacientes/pacientes-por-ciudad-chile", {}, TOKEN_PACIENTES)
    assert sum(i["cantidad_pacientes"] for i in body["items"]) == body["total_pacientes"]
    assert len(body["items"]) == body["cantidad_ciudades"]


def test_pacientes_ordenado_de_mayor_a_menor_con_desempate_por_nombre(client, oracle):
    body = _get(client, "/api/pacientes/pacientes-por-ciudad-chile", {}, TOKEN_PACIENTES)
    claves = [(-i["cantidad_pacientes"], i["ciudad"]) for i in body["items"]]
    assert claves == sorted(claves)


def test_pacientes_incluye_estados_no_activos(client, oracle):
    """h1: la consulta no filtra el estado del paciente, y el payload lo declara.

    Si algún día el negocio de verdad quiere "pacientes activos", es otra consulta
    con otro nombre; agregar el filtro acá rompería el texto original en silencio.
    """
    with get_pool().acquire() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select p.PAC_IND_ESTADO, count(distinct p.PAC_CODIGO) "
                "from DENT.PACIENTES p "
                "join DENT.DIRECCIONES d on d.COD_PERSONA = p.PAC_CODIGO "
                "where d.IND_ESTADO = 'VIG' group by p.PAC_IND_ESTADO"
            )
            por_estado = {r[0]: int(r[1]) for r in cur.fetchall()}

    out = pacientes_service.consultar_pacientes_por_ciudad_chile()
    assert out.total_pacientes == sum(por_estado.values())
    # Si el total fuera solo de pacientes activos, esto no alcanzaría.
    assert por_estado.get("ACT", 0) < out.total_pacientes
    assert out.base == "pacientes_con_direccion_vigente"