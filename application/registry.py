"""Capability Registry (V2 §10.3).

Fuente única de verdad del contrato de cada capability. Los adaptadores REST y MCP
leen de acá en vez de hardcodear descripciones, anotaciones y roles, de modo que
con varias capabilities no haya tres copias del mismo contrato que puedan divergir.

El catálogo agrupa por dominio: hoy `contabilidad.*` (bloque Control Contable) y
`pacientes.*` (censo de pacientes). Cada dominio tiene su propio router, su propio
service y su propio repository, pero todos comparten el mismo `FastMCP` y el mismo
composition root: un proceso, dos protocolos.

Reglas que este módulo garantiza por construcción (V2 R10, R17, R17b, R19):

- ``operation.mode`` es único dato de entrada; las ``annotations`` MCP se DERIVAN
  de él. No se escriben hints a mano en un decorator.
- ``description`` + ``usage_notes`` se publican al agente como contrato en prosa:
  no hay que inferir el alcance de la capability leyendo su implementación.
- El nombre del tool MCP NO lleva versión: el versionado viaja en el payload.
- Un capability ID inexistente en el catálogo no es un ``NO_DATA``: es un
  ``UNKNOWN_CAPABILITY`` (→ INVALID_ARGUMENT).
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

# Versión del contrato, no del código. R10: el nombre del tool MCP no la lleva.
CONTRACT_VERSION = 1


class OperationMode(str, Enum):
    READ = "READ"
    ANALYZE = "ANALYZE"
    ACT = "ACT"


# R17: derivación única de las anotaciones MCP a partir del modo de operación.
ANNOTATIONS_BY_MODE: dict[OperationMode, dict[str, bool]] = {
    OperationMode.READ: {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    OperationMode.ANALYZE: {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
    OperationMode.ACT: {
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    },
}

# Vocabulario de roles. Un test lo contrasta contra los tokens reales de .env,
# así un token nuevo sin capability asociada no pasa desapercibido.
KNOWN_ROLES: frozenset[str] = frozenset(
    {"contador", "analista_financiero", "gerente_finanzas", "ai_agent"}
)

_VERSION_SUFFIX = re.compile(r"[._]v\d+$")


@dataclass(frozen=True)
class CapabilityContract:
    """Contrato declarativo de una capability."""

    id: str
    name: str
    title: str
    mode: OperationMode
    description: str
    usage_notes: str
    rest_method: str
    rest_path: str
    roles: tuple[str, ...]
    oracle_sql_id: str
    legacy_method: str
    legacy_lines: str
    data_profile: str
    examples: tuple[dict[str, Any], ...]
    version: int = CONTRACT_VERSION

    @property
    def mcp_name(self) -> str:
        """Nombre del tool MCP. Sin versión (R10): la viaja el payload."""
        return self.name

    @property
    def annotations(self) -> dict[str, bool]:
        """Anotaciones MCP derivadas de ``mode`` (R17)."""
        return dict(ANNOTATIONS_BY_MODE[self.mode])

    @property
    def mcp_description(self) -> str:
        """Contrato en prosa que ve el agente: descripción + cuándo NO usarla (R17b)."""
        return f"{self.description}\n\nCuándo NO usarla: {self.usage_notes}"


CONTABILIDAD_ROLES = ("contador", "analista_financiero", "gerente_finanzas", "ai_agent")

# El dominio `pacientes` NO comparte roles con finanzas: la distribución geográfica
# de la cartera no es trabajo contable, así que `contador` queda fuera. Los tres roles
# restantes usan tokens que ya existen en .env (V2 §16.3: el dueño del
# allowed/forbidden_fields aprueba; para esta capability es gerencia).
PACIENTES_ROLES = ("analista_financiero", "gerente_finanzas", "ai_agent")

CAPABILITIES: dict[str, CapabilityContract] = {
    "contabilidad.ingresos_por_tipo_pago": CapabilityContract(
        id="contabilidad.ingresos_por_tipo_pago",
        name="consultar_ingresos_por_tipo_pago",
        title="Ingresos del día por tipo de pago",
        mode=OperationMode.READ,
        description=(
            "Consulta los ingresos del día agrupados por tipo de pago, reproduciendo la "
            "tabla 'Ingresos por tipo pago' del correo de control contable. ÚSALA cuando "
            "pregunten cuánto se recaudó hoy por tipo de pago (efectivo, tarjeta, cheque, "
            "webpay, totem, caja vecina) o cuál es el total del día. fecha es "
            "obligatoria (YYYY-MM-DD). Solo lectura."
        ),
        usage_notes=(
            "NO la uses para el detalle por tipo de tarjeta de un canal "
            "(consultar_ingresos_por_tipo_tarjeta), ni para la descomposición por "
            "previsión (consultar_ingresos_por_tipo_prevision), ni para comparar días o "
            "calcular variaciones (tool analítica), ni para el resumen de deuda "
            "(consultar_resumen_deuda)."
        ),
        rest_method="GET",
        rest_path="/api/contabilidad/ingresos-por-tipo-pago",
        roles=CONTABILIDAD_ROLES,
        oracle_sql_id="Q1",
        legacy_method="ResumenControl.setTablaIngresoPago",
        legacy_lines="200-263",
        data_profile="financial",
        examples=({"fecha": "2026-09-16"},),
    ),
    "contabilidad.resumen_deuda": CapabilityContract(
        id="contabilidad.resumen_deuda",
        name="consultar_resumen_deuda",
        title="Resumen de deuda de los últimos 4 meses",
        mode=OperationMode.READ,
        description=(
            "Devuelve la deuda promedio mensual de los últimos 4 meses contando desde el "
            "mes de `fecha` (incluido), reproduciendo la tabla 'Deuda promedio' del correo "
            "de control contable. ÚSALA cuando pregunten cómo viene la deuda o cuál fue "
            "el promedio de deuda de un mes. fecha es obligatoria (YYYY-MM-DD); solo se "
            "usan su año y mes. Solo lectura."
        ),
        usage_notes=(
            "El valor es el PROMEDIO DIARIO de deuda del mes, NO el saldo de cierre: no lo "
            "interpretes como saldo final. Los meses sin registros se omiten del "
            "resultado (pueden venir menos de 4 ítems); solo si los 4 meses están "
            "vacíos se responde NO_DATA. NO la uses para el detalle de cobranza del "
            "día (consultar_ingresos_por_tipo_pago), ni para comparar meses (tool "
            "analítica)."
        ),
        rest_method="GET",
        rest_path="/api/contabilidad/resumen-deuda",
        roles=CONTABILIDAD_ROLES,
        oracle_sql_id="Q3",
        legacy_method="ResumenControl.setTablaDeuda",
        legacy_lines="265-309",
        data_profile="financial",
        examples=({"fecha": "2017-12-15"},),
    ),
    "contabilidad.ingresos_por_tipo_tarjeta": CapabilityContract(
        id="contabilidad.ingresos_por_tipo_tarjeta",
        name="consultar_ingresos_por_tipo_tarjeta",
        title="Ingresos del día por tipo de tarjeta, por canal",
        mode=OperationMode.READ,
        description=(
            "Devuelve los ingresos con boleta de tipo TRJ del día, agrupados por tipo de "
            "tarjeta (crédito/débito) y separados por canal de origen: CAJA, TOTEM y "
            "WEBPAY. Reproduce las tres tablas de tarjeta del correo de control contable. "
            "ÚSALA cuando pregunten cuánto entró por tarjeta y de qué tipo, o comparen "
            "caja contra totem/webpay. fecha es obligatoria (YYYY-MM-DD). origen es "
            "opcional: si se omite, devuelve los tres canales. Solo lectura."
        ),
        usage_notes=(
            "Solo considera boletas activas de tipo tarjeta; el efectivo, el cheque y el "
            "webpay como forma de pago van en consultar_ingresos_por_tipo_pago. Ojo: "
            "el canal CAJA cuenta boletas con fecha exacta mientras TOTEM y WEBPAY "
            "cuentan todo el día, así que un canal vacío puede deberse a esa "
            "diferencia y no a falta de datos."
        ),
        rest_method="GET",
        rest_path="/api/contabilidad/ingresos-por-tipo-tarjeta",
        roles=CONTABILIDAD_ROLES,
        oracle_sql_id="Q10",
        legacy_method="ResumenControl.getDetIngresPorTipoTarjeta",
        legacy_lines="590-657",
        data_profile="financial",
        examples=({"fecha": "2025-05-12"}, {"fecha": "2025-05-12", "origen": "CAJA"}),
    ),
    "contabilidad.ingresos_por_tipo_prevision": CapabilityContract(
        id="contabilidad.ingresos_por_tipo_prevision",
        name="consultar_ingresos_por_tipo_prevision",
        title="Ingresos del día por tipo de previsión",
        mode=OperationMode.READ,
        description=(
            "Devuelve los ingresos del día agrupados por tipo o plan de previsión, "
            "reproduciendo la tabla 'Ingresos por tipo previsión' del correo de control "
            "contable. ÚSALA cuando pregunten en qué planes (previsiones o brackets) se "
            "concentró la recaudación del día. fecha es obligatoria (YYYY-MM-DD). Solo "
            "lectura."
        ),
        usage_notes=(
            "El listado de filas proviene de la tabla de dominio TIPO_PREVISION, por lo "
            "que las etiquetas cambian entre campañas (ej. '2024 BRACKET METALICO', "
            "'2022 Bracket Metálico'): son literales, no las consolides ni las "
            "interpretes como categorías estables. NO la uses para el desglose por tipo "
            "de pago o de tarjeta (consultar_ingresos_por_tipo_pago / "
            "consultar_ingresos_por_tipo_tarjeta)."
        ),
        rest_method="GET",
        rest_path="/api/contabilidad/ingresos-por-tipo-prevision",
        roles=CONTABILIDAD_ROLES,
        oracle_sql_id="Q11",
        legacy_method="ResumenControl.getIngresoPorPrevision",
        legacy_lines="664-695",
        data_profile="financial",
        examples=({"fecha": "2025-05-12"},),
    ),
    "contabilidad.boletas_emitidas_por_usuario": CapabilityContract(
        id="contabilidad.boletas_emitidas_por_usuario",
        name="consultar_boletas_emitidas_por_usuario",
        title="Boletas emitidas por usuario",
        mode=OperationMode.READ,
        description=(
            "Devuelve las boletas activas emitidas en el día agrupadas por usuario "
            "responsable, con cantidad y monto, reproduciendo la tabla 'Boletas por "
            "usuario' del correo de control contable. ÚSALA cuando pregunten quién emitió "
            "cuántas boletas o quién recaudó más. fecha es obligatoria (YYYY-MM-DD). Solo "
            "lectura."
        ),
        usage_notes=(
            "Devuelve PII de empleados (apellido y nombre): no la expongas a terceros sin "
            "consentimiento y cita solo los datos necesarios. El usuario con apellido '.' "
            "y nombre 'SISTEMA' agrupa las boletas emitidas por procesos automáticos, no "
            "por una persona. NO la uses para boletas anuladas/devueltas "
            "(consultar_boletas_anuladas_por_usuario)."
        ),
        rest_method="GET",
        rest_path="/api/contabilidad/boletas-emitidas-por-usuario",
        roles=CONTABILIDAD_ROLES,
        oracle_sql_id="Q8",
        legacy_method="ResumenControl.getBoletasPorUsuario",
        legacy_lines="507-544",
        data_profile="financial_pii",
        examples=({"fecha": "2025-05-12"},),
    ),
    "contabilidad.boletas_anuladas_por_usuario": CapabilityContract(
        id="contabilidad.boletas_anuladas_por_usuario",
        name="consultar_boletas_anuladas_por_usuario",
        title="Boletas anuladas, devueltas y no cobradas por usuario",
        mode=OperationMode.READ,
        description=(
            "Devuelve las boletas anuladas, devueltas o no cobradas del día agrupadas por "
            "usuario responsable, con cantidad y monto, reproduciendo la tabla 'Boletas "
            "anuladas' del correo de control contable. ÚSALA cuando pregunten cuántas "
            "boletas se anularon o devolvieron y quién las emitió. fecha es obligatoria "
            "(YYYY-MM-DD). Solo lectura."
        ),
        usage_notes=(
            "Cubre boletas anuladas, devueltas y no cobradas; no incluye pendientes ni "
            "rechazadas. Devuelve PII de empleados (apellido y nombre). IMPORTANTE: "
            "el legacy filtra por fecha exacta sin considerar la hora, así que solo "
            "cuenta las boletas registradas a las 00:00:00 y el total puede parecer "
            "bajo frente a consultar_boletas_emitidas_por_usuario. Es la semántica "
            "replicada a propósito, no un error de la capa."
        ),
        rest_method="GET",
        rest_path="/api/contabilidad/boletas-anuladas-por-usuario",
        roles=CONTABILIDAD_ROLES,
        oracle_sql_id="Q9",
        legacy_method="ResumenControl.getBoletasAnuladasPorUsuario",
        legacy_lines="547-582",
        data_profile="financial_pii",
        examples=({"fecha": "2025-05-12"},),
    ),
    "pacientes.pacientes_por_ciudad_chile": CapabilityContract(
        id="pacientes.pacientes_por_ciudad_chile",
        name="consultar_pacientes_por_ciudad_chile",
        title="Pacientes por ciudad (Chile)",
        mode=OperationMode.READ,
        description=(
            "Devuelve la cantidad de pacientes con al menos una dirección vigente, agrupada "
            "por ciudad de Chile y ordenada de mayor a menor. ÚSALA cuando pregunten cómo "
            "se reparte la cartera de pacientes entre ciudades, en qué ciudad se concentran "
            "o qué ciudades tienen más pacientes. No recibe parámetros. Solo lectura."
        ),
        usage_notes=(
            "Cuenta pacientes QUE TIENEN DIRECCIÓN VIGENTE, no pacientes activos: la "
            "consulta no filtra por el estado de la ficha, así que el resultado incluye "
            "pacientes dados de alta, inactivos y temporales. Los pacientes sin dirección "
            "vigente no aparecen en ninguna ciudad y tampoco suman al total. Los nombres "
            "de ciudad salen del maestro y vienen recortados (ej. 'SAN JOSE DE MA' es San "
            "José de Maipo), y el agrupamiento es por nombre, no por código. NO la uses "
            "para contar pacientes activos (otra consulta que esta capa no expone), ni "
            "para el detalle de una ciudad concreta o de una comuna (no acepta filtros), "
            "ni para datos clínicos, económicos o de contacto de los pacientes."
        ),
        rest_method="GET",
        rest_path="/api/pacientes/pacientes-por-ciudad-chile",
        roles=PACIENTES_ROLES,
        oracle_sql_id="ENC.PACIENTES_POR_CIUDAD",
        legacy_method="rptPacientesActivos.jsp (WebContent/dent/graph)",
        legacy_lines="112-114",
        data_profile="operational",
        examples=({},),
    ),
}


class UnknownCapabilityError(KeyError):
    """El capability ID no existe en el catálogo (→ INVALID_ARGUMENT, no NO_DATA)."""


def _validate(registry: dict[str, CapabilityContract]) -> None:
    """Invariantes del registry. Falla al importar, no en producción."""
    seen_names: set[str] = set()
    seen_paths: set[tuple[str, str]] = set()

    for cid, c in registry.items():
        if c.id != cid:
            raise ValueError(f"registry: key {cid!r} no coincide con contract.id {c.id!r}")
        if _VERSION_SUFFIX.search(c.name):
            raise ValueError(f"registry: {c.name!r} no debe llevar versión (R10)")
        if not c.description.strip():
            raise ValueError(f"registry: {c.id} sin description")
        if not c.usage_notes.strip():
            raise ValueError(f"registry: {c.id} sin usage_notes")
        if not c.examples:
            raise ValueError(f"registry: {c.id} sin examples")
        if c.name in seen_names:
            raise ValueError(f"registry: nombre MCP duplicado {c.name!r}")
        if (c.rest_method, c.rest_path) in seen_paths:
            raise ValueError(f"registry: ruta REST duplicada {c.rest_method} {c.rest_path}")
        unknown_roles = set(c.roles) - KNOWN_ROLES
        if unknown_roles:
            raise ValueError(f"registry: {c.id} con roles desconocidos {sorted(unknown_roles)}")
        if not c.roles:
            raise ValueError(f"registry: {c.id} sin roles (sería inaccesible)")
        seen_names.add(c.name)
        seen_paths.add((c.rest_method, c.rest_path))


_validate(CAPABILITIES)


def get_contract(capability_id: str) -> CapabilityContract:
    """Devuelve el contrato o falla con ``UnknownCapabilityError``."""
    try:
        return CAPABILITIES[capability_id]
    except KeyError:
        raise UnknownCapabilityError(capability_id) from None


def all_contracts() -> tuple[CapabilityContract, ...]:
    return tuple(CAPABILITIES.values())


def contracts_by_name() -> dict[str, CapabilityContract]:
    """Indexa por nombre de tool MCP (lo que el agente ve en ``list_tools``)."""
    return {c.name: c for c in CAPABILITIES.values()}