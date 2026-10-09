"""Guardas de fidelidad del SQL contra el legacy.

Estas pruebas no tocan la base: verifican que el texto SQL conserve las decisiones
que el legacy tomó, incluidas las que parecen errores. Si alguien "corrige" una de
estas formas thinking que es un bug, el suite falla y hay que ir a la ficha a
documentar el cambio a propósito.
"""

import pytest

from infrastructure.oracle.contabilidad_repository import (
    Q1_SQL,
    Q3_SQL,
    Q8_SQL,
    Q9_SQL,
    Q10_CAJA_SQL,
    Q10_SQL_BY_ORIGEN,
    Q10_TOTEM_SQL,
    Q10_WEBPAY_SQL,
    Q11_SQL,
)
from infrastructure.oracle.pacientes_repository import PACIENTES_POR_CIUDAD_CHILE_SQL


# --------------------------------------------------------------------------- #
# Q1 (sin cambios)
# --------------------------------------------------------------------------- #


def test_q1_tiene_8_bloques_y_7_union_all():
    assert Q1_SQL.count("from dent.boleta") == 4
    assert Q1_SQL.count("from dent_ciclo.boleta") == 4
    assert Q1_SQL.count("union all") == 7


def test_q1_filtra_por_id_impresora_y_estado():
    assert "id_impresora like 'IBM%'" in Q1_SQL
    assert "id_impresora = 'WPTN'" in Q1_SQL
    assert "id_impresora = 'BESTA'" in Q1_SQL
    assert "id_impresora like 'TOT%'" in Q1_SQL
    assert Q1_SQL.count("ind_estado in ('ACT')") == 8


def test_q1_usa_banda_horaria_0000_a_2359():
    assert " 00:00:00" in Q1_SQL
    assert " 23:59:59" in Q1_SQL


def test_q1_parametrizado_solo_con_fecha():
    assert ":fecha" in Q1_SQL
    assert Q1_SQL.count(":fecha") == Q1_SQL.count(" 00:00:00") + Q1_SQL.count(" 23:59:59")


def test_q1_total_consolidado_no_innova_filtros():
    assert "group by NUM_DOCTO" in Q1_SQL
    assert "TRJ" not in Q1_SQL


# --------------------------------------------------------------------------- #
# Q3 · resumen de deuda
# --------------------------------------------------------------------------- #


def test_q3_es_promedio_diario_sobre_la_misma_tabla():
    assert "round(avg(bat_deuda),0)" in Q3_SQL
    assert "from DENT.bat_deuda" in Q3_SQL


def test_q3_agrupa_por_periodo_con_bind():
    # El legacy concatenaba to_char(to_date('fecha','YYYY-MM-dd'),'YYYY-MM'). Acá va bind.
    assert "where to_char(bat_fecha,'YYYY-MM') = :periodo" in Q3_SQL
    assert Q3_SQL.count(":periodo") == 1


def test_q3_no_trae_otros_meses():
    # No hay RANGE ni BETWEEN: cada llamada es un mes exacto, la otra capa arma el loop.
    assert "between" not in Q3_SQL.lower()
    assert ">=" not in Q3_SQL
    assert "<=" not in Q3_SQL


def test_q3_no_concatena_la_entrada():
    assert "'" not in Q3_SQL.replace("'MM'", "").replace("'YYYY-MM'", "")


# --------------------------------------------------------------------------- #
# Q10 · ingresos por tipo de tarjeta
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "nombre,sql",
    [("CAJA", Q10_CAJA_SQL), ("TOTEM", Q10_TOTEM_SQL), ("WEBPAY", Q10_WEBPAY_SQL)],
)
def test_q10_cada_canal_tiene_su_propio_sql(nombre, sql):
    assert Q10_SQL_BY_ORIGEN[nombre] == sql
    assert sql.count("union all") == 1
    assert sql.count("from DENT.boleta") == 1
    assert sql.count("from DENT_CICLO.boleta") == 1
    assert "NUM_DOCTO = 'TRJ'" in sql
    assert sql.count("ind_estado = 'ACT'") == 2


@pytest.mark.parametrize(
    "nombre,sql",
    [("CAJA", Q10_CAJA_SQL), ("TOTEM", Q10_TOTEM_SQL), ("WEBPAY", Q10_WEBPAY_SQL)],
)
def test_q10_parametrizado_por_fecha_sin_concatenar(nombre, sql):
    assert sql.count(":fecha") == 2  # una vez por esquema
    assert " || " not in sql  # el legacy concatenaba; acá no


def test_q10_caja_filtra_fecha_exacta_y_ibm_duplicado():
    # h2 + h3: CAJA usa igualdad (sin trunc) y repite el filtro like 'IBM%'.
    assert "bo.FEC_BOL = to_date(:fecha,'YYYY-MM-DD')" in Q10_CAJA_SQL
    assert "trunc(" not in Q10_CAJA_SQL
    assert Q10_CAJA_SQL.count("bo.id_impresora like 'IBM%'") == 4  # 2 por esquema


@pytest.mark.parametrize("sql", [Q10_TOTEM_SQL, Q10_WEBPAY_SQL])
def test_q10_totem_y_webpay_filtran_por_trunc(sql):
    # h2: TOTEM y WEBPAY usan trunc(FEC_BOL), a diferencia de CAJA.
    assert "trunc(bo.FEC_BOL) = to_date(:fecha,'YYYY-MM-DD')" in sql
    assert "bo.FEC_BOL = to_date" not in sql


def test_q10_literales_de_canal():
    assert "bo.id_impresora like 'TOT%'" in Q10_TOTEM_SQL
    assert "bo.id_impresora = 'WPTN'" in Q10_WEBPAY_SQL
    assert "TOT%" not in Q10_WEBPAY_SQL
    assert "WPTN" not in Q10_TOTEM_SQL


def test_q10_decode_solo_en_totem_y_webpay():
    # El legacy NO aplica decode en CAJA: ahí devuelve el código crudo.
    decode = "decode(codigo,'CRD1','CREDITO','DEB1','DEBITO',codigo)"
    assert decode in Q10_TOTEM_SQL
    assert decode in Q10_WEBPAY_SQL
    assert "decode(" not in Q10_CAJA_SQL


def test_q10_devuelve_codigo_crudo_en_los_tres_canales():
    # Diferencia deliberada: la columna extra no cambia qué filas se agrupan.
    for sql in (Q10_CAJA_SQL, Q10_TOTEM_SQL, Q10_WEBPAY_SQL):
        assert "codigo codigo_tarjeta" in sql
        assert "group by codigo" in sql


def test_q10_no_agrupa_por_alias_de_select():
    # Oracle no resuelve alias de SELECT en GROUP BY (ORA-00904): agrupar por `codigo`.
    for sql in (Q10_CAJA_SQL, Q10_TOTEM_SQL, Q10_WEBPAY_SQL):
        assert "group by tipo" not in sql


# --------------------------------------------------------------------------- #
# Q11 · ingresos por tipo de previsión
# --------------------------------------------------------------------------- #


def test_q11_usa_banda_horaria_y_union_de_dos_esquemas():
    assert " 00:00:00" in Q11_SQL
    assert " 23:59:59" in Q11_SQL
    assert Q11_SQL.count("union all") == 1


def test_q11_joins_por_prevision_con_owner_explicito():
    # h6: el legacy escribía fichas/dominio sin prefijo y dependía del owner de sesión.
    assert "DENT.fichas" in Q11_SQL
    assert "DENT.dominio" in Q11_SQL
    assert "bo.NUM_FICHA = fi.NUM_FICHA" in Q11_SQL
    assert "fi.TIP_PREVISION = do.DOMICODIGO" in Q11_SQL
    assert "do.DOMINOMBRE = 'TIPO_PREVISION'" in Q11_SQL


def test_q11_orden_deterministico_por_descripcion():
    assert "order by DOMIDESCRI" in Q11_SQL
    assert "group by DOMIDESCRI" in Q11_SQL


# --------------------------------------------------------------------------- #
# Q8 · boletas emitidas por usuario
# --------------------------------------------------------------------------- #


def test_q8_usa_banda_horaria_y_solo_activas():
    assert " 00:00:00" in Q8_SQL
    assert " 23:59:59" in Q8_SQL
    assert Q8_SQL.count("bo.ind_estado = 'ACT'") == 2
    assert Q8_SQL.count("union all") == 1


def test_q8_agrupa_por_apellido_y_nombre():
    assert "group by USUAPEP, USUNOMC" in Q8_SQL
    assert "bo.COD_USUARIO = us.USULOGIN" in Q8_SQL


def test_q8_no_selecciona_rut():
    # PII: el RUT no debe viajar al contrato (V2 R12).
    assert "USURUT" not in Q8_SQL


def test_q8_no_tiene_order_by():
    # El legacy no ordena; el orden canónico lo aplica el service.
    assert "order by" not in Q8_SQL.lower()


# --------------------------------------------------------------------------- #
# Q9 · boletas anuladas por usuario
# --------------------------------------------------------------------------- #


def test_q9_filtra_fecha_exacta_sin_trunc():
    # h2 DELIBERADO: solo cuenta boletas con hora 00:00:00. No "arreglarlo".
    assert "bo.FEC_BOL = to_date(:fecha,'YYYY-MM-DD')" in Q9_SQL
    assert "trunc(" not in Q9_SQL


def test_q9_estados_anu_dev_nci():
    assert Q9_SQL.count("bo.ind_estado in ('ANU', 'DEV', 'NCI')") == 2
    assert "PND" not in Q9_SQL
    assert "NCR" not in Q9_SQL


def test_q9_no_tiene_banda_horaria():
    assert " 00:00:00" not in Q9_SQL
    assert " 23:59:59" not in Q9_SQL


def test_q9_no_selecciona_rut():
    assert "USURUT" not in Q9_SQL


# --------------------------------------------------------------------------- #
# ENC.PACIENTES_POR_CIUDAD · pacientes por ciudad (dominio pacientes)
# --------------------------------------------------------------------------- #


def test_pacientes_no_filtra_el_estado_del_paciente():
    # La "corrección" más probable y equivocada de esta consulta es agregar
    # `and p.PAC_IND_ESTADO = 'ACT'` para que diga "pacientes activos". No lo es:
    # cuenta pacientes con dirección vigente. El texto original no filtra y la
    # ficha dice que no se agrega el filtro.
    assert "PAC_IND_ESTADO" not in PACIENTES_POR_CIUDAD_CHILE_SQL
    assert "ind_estado = 'ACT'" not in PACIENTES_POR_CIUDAD_CHILE_SQL


def test_pacientes_filtra_solo_direcciones_vigentes():
    assert PACIENTES_POR_CIUDAD_CHILE_SQL.count("d.IND_ESTADO = 'VIG'") == 1
    assert PACIENTES_POR_CIUDAD_CHILE_SQL.lower().count("where") == 1


def test_pacientes_agrupa_por_nombre_de_ciudad_y_cuenta_distintos():
    assert "count(distinct p.PAC_CODIGO)" in PACIENTES_POR_CIUDAD_CHILE_SQL
    assert "group by ci.NOM_CIU" in PACIENTES_POR_CIUDAD_CHILE_SQL
    # Agrupar por código daría una fila por ciudad lógica; el texto agrupa por
    # nombre, y eso también decide cómo se ven los nombres recortados del maestro.
    assert "group by ci.COD_CIU" not in PACIENTES_POR_CIUDAD_CHILE_SQL


def test_pacientes_une_las_tres_tablas_con_owner_explicito():
    sql = PACIENTES_POR_CIUDAD_CHILE_SQL
    assert "from DENT.PACIENTES p" in sql
    assert "join DENT.DIRECCIONES d on d.COD_PERSONA = p.PAC_CODIGO" in sql
    assert "join DENT.CIUDADES ci on ci.COD_CIU = d.COD_CIUDAD" in sql
    # Inner joins a propósito: quien no tiene dirección vigente, o cuya ciudad no
    # existe en el maestro, no aparece en ninguna fila.
    assert "left join" not in sql.lower()
    assert "outer join" not in sql.lower()


def test_pacientes_no_selecciona_identificadores_de_paciente():
    # V2 R12: el conteo viaja agregado, nunca la lista de pacientes.
    sql = PACIENTES_POR_CIUDAD_CHILE_SQL
    for prohibido in ("p.PAC_CODIGO,", "p.PAC_RUT", "USURUT", "select p."):
        assert prohibido not in sql, f"la consulta expone {prohibido!r}"


def test_pacientes_tiene_orden_deterministico():
    # La capa no reordena: confía en un orden total del SQL. Sin el desempate por
    # nombre, dos ciudades empatadas podrían cambiar de posición entre llamadas.
    assert "order by cantidad_pacientes desc, ci.NOM_CIU" in PACIENTES_POR_CIUDAD_CHILE_SQL


def test_pacientes_no_tiene_parametros():
    # No hay binds ni fecha: si aparece un `:algo`, es una capacidad nueva y esto
    # tiene que revisarse a propósito.
    sql = PACIENTES_POR_CIUDAD_CHILE_SQL
    assert ":" not in sql
    assert "to_date" not in sql.lower()
    assert " || " not in sql


# --------------------------------------------------------------------------- #
# Transversales
# --------------------------------------------------------------------------- #


ALL_SQL = {
    "Q1": Q1_SQL,
    "Q3": Q3_SQL,
    "Q10_CAJA": Q10_CAJA_SQL,
    "Q10_TOTEM": Q10_TOTEM_SQL,
    "Q10_WEBPAY": Q10_WEBPAY_SQL,
    "Q11": Q11_SQL,
    "Q8": Q8_SQL,
    "Q9": Q9_SQL,
    "ENC.PACIENTES_POR_CIUDAD": PACIENTES_POR_CIUDAD_CHILE_SQL,
}


@pytest.mark.parametrize("nombre,sql", sorted(ALL_SQL.items()))
def test_ninguna_query_concatena_la_entrada(nombre, sql):
    """El input nunca puede terminar dentro del texto del SQL.

    Concatenar un literal de hora al bind (:fecha || ' 00:00:00') sí está bien:
    arma un valor de fecha, no una sentencia. Lo que no puede pasar es que la
    fecha del usuario aparezca incrustada en el SQL.
    """
    import re

    # Una fecha real incrustada en el texto sería un YYYY-MM-DD con dígitos.
    assert not re.search(r"\d{4}-\d{2}-\d{2}", sql), f"{nombre} tiene una fecha incrustada"

    # El primer argumento de todo to_date(...) debe ser un bind, no un literal con datos.
    for args in re.findall(r"to_date\(([^)]*)\)", sql):
        primero = args.split(",")[0].strip()
        assert primero.startswith(":"), f"{nombre}: to_date con argumento no-bind: {primero!r}"

    for prohibido in ("qryFecha", "fechaCns"):
        assert prohibido not in sql, f"{nombre} usa un nombre de variable del legacy"


@pytest.mark.parametrize("nombre,sql", sorted(ALL_SQL.items()))
def test_toda_tabla_de_boleta_lleva_owner_explicito(nombre, sql):
    # h6: nada de tablas sin prefijo que dependan del owner por defecto de la sesión.
    import re

    for tabla in re.findall(r"from\s+([a-z_]+)\.boleta", sql, flags=re.IGNORECASE):
        assert tabla.upper() in {"DENT", "DENT_CICLO"}, f"{nombre} usa owner inesperado: {tabla}"


@pytest.mark.parametrize("nombre,sql", sorted(ALL_SQL.items()))
def test_todas_las_consultas_son_select_y_no_modifican(nombre, sql):
    assert sql.strip().lower().startswith("select")
    for prohibido in ("insert ", "update ", "delete ", "merge ", "drop ", "alter "):
        assert prohibido not in sql.lower(), f"{nombre} no debe modificar datos"