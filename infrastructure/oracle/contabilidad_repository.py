from datetime import date
from decimal import Decimal

import oracledb

from application.contabilidad.ports import (
    BoletaPorUsuarioRow,
    ContabilidadPort,
    DeudaRow,
    IngresoRow,
    PrevisionRow,
    TarjetaRow,
)
from application.errors import InfrastructureError
from database import get_pool

Q1_SQL = """
select NUM_DOCTO tipo_doc, sum(mto_bol) mto from (
  select NUM_DOCTO, mto_bol
  from dent.boleta
  where fec_bol >= to_date(:fecha || ' 00:00:00','YYYY-MM-DD HH24:MI:SS')
    and fec_bol <= to_date(:fecha || ' 23:59:59','YYYY-MM-DD HH24:MI:SS')
    and id_impresora like 'IBM%'
    and ind_estado in ('ACT')
  union all
  select NUM_DOCTO, mto_bol
  from dent_ciclo.boleta
  where fec_bol >= to_date(:fecha || ' 00:00:00','YYYY-MM-DD HH24:MI:SS')
    and fec_bol <= to_date(:fecha || ' 23:59:59','YYYY-MM-DD HH24:MI:SS')
    and ind_estado in ('ACT')
    and id_impresora like 'IBM%'
  union all
  select 'WEBPAY' NUM_DOCTO, mto_bol
  from dent.boleta
  where fec_bol >= to_date(:fecha || ' 00:00:00','YYYY-MM-DD HH24:MI:SS')
    and fec_bol <= to_date(:fecha || ' 23:59:59','YYYY-MM-DD HH24:MI:SS')
    and ind_estado in ('ACT')
    and id_impresora = 'WPTN'
  union all
  select 'WEBPAY' NUM_DOCTO, mto_bol
  from dent_ciclo.boleta
  where fec_bol >= to_date(:fecha || ' 00:00:00','YYYY-MM-DD HH24:MI:SS')
    and fec_bol <= to_date(:fecha || ' 23:59:59','YYYY-MM-DD HH24:MI:SS')
    and ind_estado in ('ACT')
    and id_impresora = 'WPTN'
  union all
  select 'CAJA VECINA BCO.EST.' NUM_DOCTO, mto_bol
  from dent.boleta
  where fec_bol >= to_date(:fecha || ' 00:00:00','YYYY-MM-DD HH24:MI:SS')
    and fec_bol <= to_date(:fecha || ' 23:59:59','YYYY-MM-DD HH24:MI:SS')
    and ind_estado in ('ACT')
    and id_impresora = 'BESTA'
  union all
  select 'CAJA VECINA BCO.EST.' NUM_DOCTO, mto_bol
  from dent_ciclo.boleta
  where fec_bol >= to_date(:fecha || ' 00:00:00','YYYY-MM-DD HH24:MI:SS')
    and fec_bol <= to_date(:fecha || ' 23:59:59','YYYY-MM-DD HH24:MI:SS')
    and ind_estado in ('ACT')
    and id_impresora = 'BESTA'
  union all
  select 'TOTEM' NUM_DOCTO, mto_bol
  from dent.boleta
  where fec_bol >= to_date(:fecha || ' 00:00:00','YYYY-MM-DD HH24:MI:SS')
    and fec_bol <= to_date(:fecha || ' 23:59:59','YYYY-MM-DD HH24:MI:SS')
    and ind_estado in ('ACT')
    and id_impresora like 'TOT%'
  union all
  select 'TOTEM' NUM_DOCTO, mto_bol
  from dent_ciclo.boleta
  where fec_bol >= to_date(:fecha || ' 00:00:00','YYYY-MM-DD HH24:MI:SS')
    and fec_bol <= to_date(:fecha || ' 23:59:59','YYYY-MM-DD HH24:MI:SS')
    and ind_estado in ('ACT')
    and id_impresora like 'TOT%'
) group by NUM_DOCTO
"""

# Q3 · setTablaDeuda (ResumenControl.java:265-309)
#
# El legacy concatena "to_char(to_date('"+fechaCns+"','YYYY-MM-dd'),'YYYY-MM')"
# dentro del WHERE, 4 veces en un loop. Acá el período viaja como bind y el
# service replica el loop, conservando los 4 viajes a Oracle.
#
# round(avg(...),0) es el PROMEDIO DIARIO de deuda del mes, no el saldo de cierre.
Q3_SQL = """
select to_char(bat_fecha,'MM') mes, round(avg(bat_deuda),0) deuda
from DENT.bat_deuda
where to_char(bat_fecha,'YYYY-MM') = :periodo
group by to_char(bat_fecha,'MM')
"""

# Q10 · getDetIngresPorTipoTarjeta (ResumenControl.java:590-657)
#
# El legacy tiene TRES queries distintas según el canal (qryCaja / qryTotem /
# qryWebpay), con dos diferencias que se replican a propósito:
#
#   1. CAJA filtra por FEC_BOL exacto; TOTEM y WEBPAY por trunc(FEC_BOL).
#   2. CAJA filtra id_impresora like 'IBM%' DOS veces (redundante pero inocuo);
#      TOTEM like 'TOT%' y WEBPAY = 'WPTN'.
#   3. Solo TOTEM y WEBPAY aplican decode de TIP_TARJETA (CRD1→CREDITO,
#      DEB1→DEBITO) en el SQL; CAJA devuelve el código crudo.
#
# Diferencia deliberada respecto del legacy: además del tipo se selecciona el
# código crudo (codigo_tarjeta). El decode es función determinista del código, así
# que agrupar por `codigo` produce exactamente los mismos grupos que el
# `group by tipo` del legacy; la columna extra solo permite exponer el valor crudo
# sin perder la etiqueta que muestra el correo en cada canal. Oracle no resuelve un
# alias de SELECT dentro del GROUP BY, de ahí que se agrupe por la columna real.

Q10_CAJA_SQL = """
select codigo tipo, codigo codigo_tarjeta, count(1) cantidad, sum(mto_bol) monto from (
  select bo.TIP_TARJETA codigo, bo.mto_bol
  from DENT.boleta bo
  where bo.FEC_BOL = to_date(:fecha,'YYYY-MM-DD')
    and bo.NUM_DOCTO = 'TRJ'
    and bo.ind_estado = 'ACT'
    and bo.id_impresora like 'IBM%'
    and bo.id_impresora like 'IBM%'
  union all
  select bo.TIP_TARJETA, bo.mto_bol
  from DENT_CICLO.boleta bo
  where bo.FEC_BOL = to_date(:fecha,'YYYY-MM-DD')
    and bo.NUM_DOCTO = 'TRJ'
    and bo.ind_estado = 'ACT'
    and bo.id_impresora like 'IBM%'
    and bo.id_impresora like 'IBM%'
) group by codigo
"""

Q10_TOTEM_SQL = """
select decode(codigo,'CRD1','CREDITO','DEB1','DEBITO',codigo) tipo,
       codigo codigo_tarjeta,
       count(1) cantidad,
       sum(mto_bol) monto
from (
  select bo.TIP_TARJETA codigo, bo.mto_bol
  from DENT.boleta bo
  where trunc(bo.FEC_BOL) = to_date(:fecha,'YYYY-MM-DD')
    and bo.NUM_DOCTO = 'TRJ'
    and bo.ind_estado = 'ACT'
    and bo.id_impresora like 'TOT%'
  union all
  select bo.TIP_TARJETA, bo.mto_bol
  from DENT_CICLO.boleta bo
  where trunc(bo.FEC_BOL) = to_date(:fecha,'YYYY-MM-DD')
    and bo.NUM_DOCTO = 'TRJ'
    and bo.ind_estado = 'ACT'
    and bo.id_impresora like 'TOT%'
) group by codigo
"""

Q10_WEBPAY_SQL = """
select decode(codigo,'CRD1','CREDITO','DEB1','DEBITO',codigo) tipo,
       codigo codigo_tarjeta,
       count(1) cantidad,
       sum(mto_bol) monto
from (
  select bo.TIP_TARJETA codigo, bo.mto_bol
  from DENT.boleta bo
  where trunc(bo.FEC_BOL) = to_date(:fecha,'YYYY-MM-DD')
    and bo.NUM_DOCTO = 'TRJ'
    and bo.ind_estado = 'ACT'
    and bo.id_impresora = 'WPTN'
  union all
  select bo.TIP_TARJETA, bo.mto_bol
  from DENT_CICLO.boleta bo
  where trunc(bo.FEC_BOL) = to_date(:fecha,'YYYY-MM-DD')
    and bo.NUM_DOCTO = 'TRJ'
    and bo.ind_estado = 'ACT'
    and bo.id_impresora = 'WPTN'
) group by codigo
"""

Q10_SQL_BY_ORIGEN = {
    "CAJA": Q10_CAJA_SQL,
    "TOTEM": Q10_TOTEM_SQL,
    "WEBPAY": Q10_WEBPAY_SQL,
}

# Q11 · getIngresoPorPrevision (ResumenControl.java:664-695)
#
# El legacy escribe las tablas sin prefijo (boleta, fichas, dominio), o sea que
# dependía del owner por defecto de la sesión. Acá se fija DENT.* explícito (R19 h6).
Q11_SQL = """
select DOMIDESCRI, count(1) cantidad, sum(mto_bol) monto from (
  select do.DOMIDESCRI, bo.mto_bol
  from DENT.boleta bo, DENT.fichas fi, DENT.dominio do
  where bo.fec_bol >= to_date(:fecha || ' 00:00:00','YYYY-MM-DD HH24:MI:SS')
    and bo.fec_bol <= to_date(:fecha || ' 23:59:59','YYYY-MM-DD HH24:MI:SS')
    and bo.NUM_FICHA = fi.NUM_FICHA
    and bo.ind_estado = 'ACT'
    and fi.TIP_PREVISION = do.DOMICODIGO
    and do.DOMINOMBRE = 'TIPO_PREVISION'
  union all
  select do.DOMIDESCRI, bo.mto_bol
  from DENT_CICLO.boleta bo, DENT.fichas fi, DENT.dominio do
  where bo.fec_bol >= to_date(:fecha || ' 00:00:00','YYYY-MM-DD HH24:MI:SS')
    and bo.fec_bol <= to_date(:fecha || ' 23:59:59','YYYY-MM-DD HH24:MI:SS')
    and bo.NUM_FICHA = fi.NUM_FICHA
    and bo.ind_estado = 'ACT'
    and fi.TIP_PREVISION = do.DOMICODIGO
    and do.DOMINOMBRE = 'TIPO_PREVISION'
) group by DOMIDESCRI order by DOMIDESCRI
"""

# Q8 · getBoletasPorUsuario (ResumenControl.java:507-544)
#
# El legacy no tiene ORDER BY: el orden es el que Oracle devuelva. Esta capa
# ordena en el service (orden canónico), por eso el SQL tampoco lo lleva.
Q8_SQL = """
select USUAPEP, USUNOMC, count(1) cantidad, sum(mto_bol) monto from (
  select us.USUAPEP, us.USUNOMC, bo.mto_bol
  from DENT.boleta bo, DENT.usuarios us
  where bo.fec_bol >= to_date(:fecha || ' 00:00:00','YYYY-MM-DD HH24:MI:SS')
    and bo.fec_bol <= to_date(:fecha || ' 23:59:59','YYYY-MM-DD HH24:MI:SS')
    and bo.ind_estado = 'ACT'
    and bo.COD_USUARIO = us.USULOGIN
  union all
  select us.USUAPEP, us.USUNOMC, bo.mto_bol
  from DENT_CICLO.boleta bo, DENT.usuarios us
  where bo.fec_bol >= to_date(:fecha || ' 00:00:00','YYYY-MM-DD HH24:MI:SS')
    and bo.fec_bol <= to_date(:fecha || ' 23:59:59','YYYY-MM-DD HH24:MI:SS')
    and bo.ind_estado = 'ACT'
    and bo.COD_USUARIO = us.USULOGIN
) group by USUAPEP, USUNOMC
"""

# Q9 · getBoletasAnuladasPorUsuario (ResumenControl.java:547-582)
#
# Dos diferencias con Q8, ambas deliberadas:
#   1. FEC_BOL = to_date(:fecha,'YYYY-MM-DD') EXACTO, sin trunc. El legacy
#      concatena la fecha entre comillas, así que solo cuenta boletas con hora
#      00:00:00. Se replica tal cual (R19 h2).
#   2. Estados ANU, DEV y NCI en vez de solo ACT.
Q9_SQL = """
select USUAPEP, USUNOMC, count(1) cantidad, sum(mto_bol) monto from (
  select us.USUAPEP, us.USUNOMC, bo.mto_bol
  from DENT.boleta bo, DENT.usuarios us
  where bo.FEC_BOL = to_date(:fecha,'YYYY-MM-DD')
    and bo.ind_estado in ('ANU', 'DEV', 'NCI')
    and bo.COD_USUARIO = us.USULOGIN
  union all
  select us.USUAPEP, us.USUNOMC, bo.mto_bol
  from DENT_CICLO.boleta bo, DENT.usuarios us
  where bo.FEC_BOL = to_date(:fecha,'YYYY-MM-DD')
    and bo.ind_estado in ('ANU', 'DEV', 'NCI')
    and bo.COD_USUARIO = us.USULOGIN
) group by USUAPEP, USUNOMC
"""


class ContabilidadRepository(ContabilidadPort):
    """Adapter Oracle. SQL idéntico al legacy (Q1 · setTablaIngresoPago),
    con fecha por bind parameter y owner de esquema explícito (V2 §19 h6)."""

    Q1_SQL = Q1_SQL
    Q3_SQL = Q3_SQL
    Q10_SQL_BY_ORIGEN = Q10_SQL_BY_ORIGEN
    Q11_SQL = Q11_SQL
    Q8_SQL = Q8_SQL
    Q9_SQL = Q9_SQL

    def __init__(self, pool: oracledb.ConnectionPool | None = None):
        self._pool = pool

    @property
    def pool(self) -> oracledb.ConnectionPool:
        return self._pool or get_pool()

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _fetchall(self, sql: str, **binds):
        """Ejecuta y devuelve filas crudas. Traduce cualquier fallo a UNAVAILABLE:
        una caída de Oracle jamás debe disfrazarse de 'tabla vacía'."""
        try:
            with self.pool.acquire() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, **binds)
                    return cur.fetchall()
        except Exception as exc:
            raise InfrastructureError() from exc

    # ------------------------------------------------------------------ #
    # #2 · Q1
    # ------------------------------------------------------------------ #

    def ingresos_por_tipo_pago(self, fecha: date) -> list[IngresoRow]:
        filas = self._fetchall(self.Q1_SQL, fecha=fecha.isoformat())
        return [IngresoRow(tipo_pago=str(r[0]), monto=Decimal(str(r[1]))) for r in filas]

    # ------------------------------------------------------------------ #
    # #1 · Q3
    # ------------------------------------------------------------------ #

    def deuda_del_mes(self, periodo: str) -> DeudaRow | None:
        filas = self._fetchall(self.Q3_SQL, periodo=periodo)
        if not filas:
            return None
        r = filas[0]
        return DeudaRow(mes=str(r[0]), deuda=Decimal(str(r[1])))

    # ------------------------------------------------------------------ #
    # #3 · Q10
    # ------------------------------------------------------------------ #

    def ingresos_por_tipo_tarjeta(self, fecha: date, origen: str) -> list[TarjetaRow]:
        try:
            sql = self.Q10_SQL_BY_ORIGEN[origen]
        except KeyError:
            raise ValueError(f"origen no soportado: {origen!r}") from None
        filas = self._fetchall(sql, fecha=fecha.isoformat())
        return [
            TarjetaRow(
                tipo=str(r[0]),
                codigo=str(r[1]),
                cantidad=int(r[2]),
                monto=Decimal(str(r[3])),
            )
            for r in filas
        ]

    # ------------------------------------------------------------------ #
    # #4 · Q11
    # ------------------------------------------------------------------ #

    def ingresos_por_tipo_prevision(self, fecha: date) -> list[PrevisionRow]:
        filas = self._fetchall(self.Q11_SQL, fecha=fecha.isoformat())
        return [
            PrevisionRow(prevision=str(r[0]), cantidad=int(r[1]), monto=Decimal(str(r[2])))
            for r in filas
        ]

    # ------------------------------------------------------------------ #
    # #5 · Q8
    # ------------------------------------------------------------------ #

    def boletas_por_usuario(self, fecha: date) -> list[BoletaPorUsuarioRow]:
        filas = self._fetchall(self.Q8_SQL, fecha=fecha.isoformat())
        return [
            BoletaPorUsuarioRow(
                apellido=str(r[0]),
                nombre=str(r[1]),
                cantidad=int(r[2]),
                monto=Decimal(str(r[3])),
            )
            for r in filas
        ]

    # ------------------------------------------------------------------ #
    # #6 · Q9
    # ------------------------------------------------------------------ #

    def boletas_anuladas_por_usuario(self, fecha: date) -> list[BoletaPorUsuarioRow]:
        filas = self._fetchall(self.Q9_SQL, fecha=fecha.isoformat())
        return [
            BoletaPorUsuarioRow(
                apellido=str(r[0]),
                nombre=str(r[1]),
                cantidad=int(r[2]),
                monto=Decimal(str(r[3])),
            )
            for r in filas
        ]