import oracledb

from application.errors import InfrastructureError
from application.pacientes.ports import PacientePorCiudadRow, PacientesPort
from database import get_pool

# ENC.PACIENTES_POR_CIUDAD · docs/go/encuentros.md §"Cantidad de pacientes por ciudad"
#
# Es la única consulta de este bloque y NO viene del Control Contable, así que no
# tiene ni banda horaria ni unión con la réplica: es un censo de la cartera.
#
# Decisiones del texto original que se replican tal cual (V2 §0.1, no innovar):
#
#   1. NO filtra por el estado del paciente. Cuenta toda ficha que tenga una
#      dirección vigente, incluidos pacientes dados de alta, inactivos y
#      temporales. No es "pacientes activos".
#   2. Solo filtra DENT.DIRECCIONES.IND_ESTADO = 'VIG'. Los joins son internos, así
#      que un paciente sin dirección vigente —o cuya ciudad no exista en el maestro—
#      no aparece en ninguna ciudad y tampoco suma al total.
#   3. Agrupa por NOM_CIU (nombre), no por COD_CIU. Dos códigos con el mismo
#      nombre se fusionarían en una fila. En QA no hay nombres repetidos (verificado).
#   4. COUNT(DISTINCT PAC_CODIGO): un paciente con varias direcciones vigentes en la
#      misma ciudad cuenta una vez. El total por ciudad puede por eso sumar más que
#      la cantidad de pacientes distintos.
#
# No lleva parámetros, así que no hay bind que parametrizar: el repo no concatena nada.
PACIENTES_POR_CIUDAD_CHILE_SQL = """
select ci.NOM_CIU ciudad,
       count(distinct p.PAC_CODIGO) cantidad_pacientes
from DENT.PACIENTES p
join DENT.DIRECCIONES d on d.COD_PERSONA = p.PAC_CODIGO
join DENT.CIUDADES ci on ci.COD_CIU = d.COD_CIUDAD
where d.IND_ESTADO = 'VIG'
group by ci.NOM_CIU
order by cantidad_pacientes desc, ci.NOM_CIU
"""


class PacientesRepository(PacientesPort):
    """Adapter Oracle del bloque Pacientes."""

    PACIENTES_POR_CIUDAD_CHILE_SQL = PACIENTES_POR_CIUDAD_CHILE_SQL

    def __init__(self, pool: oracledb.ConnectionPool | None = None):
        self._pool = pool

    @property
    def pool(self) -> oracledb.ConnectionPool:
        return self._pool or get_pool()

    def _fetchall(self, sql: str, **binds):
        """Igual que en el bloque contable: cualquier fallo es UNAVAILABLE, nunca
        una lista vacía que el agente lea como 'no hay pacientes'."""
        try:
            with self.pool.acquire() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, **binds)
                    return cur.fetchall()
        except Exception as exc:
            raise InfrastructureError() from exc

    def pacientes_por_ciudad_chile(self) -> list[PacientePorCiudadRow]:
        filas = self._fetchall(self.PACIENTES_POR_CIUDAD_CHILE_SQL)
        # NOM_CIU admite nulos en el maestro; hoy no hay ninguno, pero un None
        # terminaría serializado como la cadena "None" en el payload del agente.
        return [
            PacientePorCiudadRow(
                ciudad="" if r[0] is None else str(r[0]),
                cantidad_pacientes=int(r[1]),
            )
            for r in filas
        ]
