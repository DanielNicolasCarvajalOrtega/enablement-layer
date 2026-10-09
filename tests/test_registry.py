import asyncio
import re
from pathlib import Path

import pytest

from adapters.mcp.contabilidad import mcp
from application.registry import (
    ANNOTATIONS_BY_MODE,
    CAPABILITIES,
    KNOWN_ROLES,
    OperationMode,
    UnknownCapabilityError,
    all_contracts,
    contracts_by_name,
    get_contract,
)
from config import settings

VERSION_SUFFIX = re.compile(r"[._]v\d+$")


@pytest.fixture(scope="module")
def tools():
    import adapters.mcp.pacientes  # noqa: F401  · registra las tools del dominio pacientes

    return asyncio.run(mcp.list_tools())


# Declaración explícita de la forma de entrada de cada capability, por id.
# NO se deduce del prefijo del dominio: un dominio nuevo con `fecha` caería en el
# grupo equivocado y el test de "sin argumentos" fallaría con un mensaje que manda
# a revisar el schema cuando el problema es esta clasificación.
CON_FECHA = (
    "contabilidad.ingresos_por_tipo_pago",
    "contabilidad.resumen_deuda",
    "contabilidad.ingresos_por_tipo_tarjeta",
    "contabilidad.ingresos_por_tipo_prevision",
    "contabilidad.boletas_emitidas_por_usuario",
    "contabilidad.boletas_anuladas_por_usuario",
)
SIN_ARGUMENTOS = ("pacientes.pacientes_por_ciudad_chile",)


def test_toda_capability_declara_si_toma_argumentos():
    declaradas = set(CON_FECHA) | set(SIN_ARGUMENTOS)
    assert declaradas == set(CAPABILITIES), (
        f"capabilities sin declarar su forma de entrada: "
        f"{sorted(set(CAPABILITIES) - declaradas)}"
    )
    assert set(CON_FECHA) & set(SIN_ARGUMENTOS) == set()


# --------------------------------------------------------------------------- #
# Invariantes del contrato (Nivel 3, R10 / R17 / R17b)
# --------------------------------------------------------------------------- #


def test_catalogo_documenta_todas_las_capabilities():
    # Tripwire de documentación (antes: `len(CAPABILITIES) == 7`).
    # El conteo hardcodeado forzaba a actualizar el catálogo, pero no lo verificaba
    # y además había que recordar subirlo a mano. Acá se comprueba contra el archivo
    # real: agregar una capability sin su fila y su ficha queda en verde imposible.
    catálogo = Path(__file__).resolve().parents[2] / (
        "docs/refactorizacion/capacidades/CATALOGO.md"
    )
    if not catálogo.exists():
        pytest.fail(
            f"No encuentro el catálogo en {catálogo}. Se resuelve respecto de este "
            "archivo, no del cwd: la capa y docs/ viven hermanas en el repo."
        )
    texto = catálogo.read_text(encoding="utf-8")
    # El tool_name del contrato es lo que el catálogo enlaza como nombre MCP.
    no_documentadas = sorted(c.name for c in all_contracts() if c.name not in texto)
    assert not no_documentadas, (
        f"capabilities sin fila en {catálogo.name}: {no_documentadas}. "
        "Completá la tabla resumen, el índice 'Cómo elegir' y la ficha."
    )


@pytest.mark.parametrize("cid", sorted(CAPABILITIES))
def test_nombre_mcp_no_lleva_version(cid):
    # R10: el versionado viaja en el payload, no en el nombre del tool.
    assert not VERSION_SUFFIX.search(get_contract(cid).name)


@pytest.mark.parametrize("cid", sorted(CAPABILITIES))
def test_contracto_tiene_description_usage_notes_y_ejemplos(cid):
    # R17b: el agente no debe inferir el alcance leyendo la implementación.
    c = get_contract(cid)
    assert c.description.strip()
    assert c.usage_notes.strip()
    assert c.examples


@pytest.mark.parametrize("cid", sorted(CAPABILITIES))
def test_mcp_description_concatena_description_y_usage_notes(cid):
    c = get_contract(cid)
    assert c.mcp_description == f"{c.description}\n\nCuándo NO usarla: {c.usage_notes}"


@pytest.mark.parametrize("cid", sorted(CAPABILITIES))
def test_annotations_se_derivan_del_modo(cid):
    # R17: las annotations nunca se escriben a mano.
    c = get_contract(cid)
    assert c.annotations == ANNOTATIONS_BY_MODE[c.mode]


@pytest.mark.parametrize("cid", sorted(CAPABILITIES))
def test_roles_conocidos_y_no_vacios(cid):
    c = get_contract(cid)
    assert c.roles
    assert set(c.roles) <= KNOWN_ROLES


def test_todas_las_capabilities_son_read():
    # Fase 1 del proyecto: solo lectura.
    assert {c.mode for c in all_contracts()} == {OperationMode.READ}


def test_capability_inexistente_falla_como_unknown():
    # Un id desconocido no es NO_DATA: es INVALID_ARGUMENT.
    with pytest.raises(UnknownCapabilityError):
        get_contract("contabilidad.no_existe")


def test_nombres_y_rutas_son_unicos():
    names = [c.name for c in all_contracts()]
    paths = [(c.rest_method, c.rest_path) for c in all_contracts()]
    assert len(set(names)) == len(names)
    assert len(set(paths)) == len(paths)


def test_contratos_por_nombre_incluye_a_todos():
    assert set(contracts_by_name()) == {c.name for c in all_contracts()}


def test_roles_de_pacientes_son_los_tres_aprobados_y_no_el_contador():
    # Decisión dedueña: la distribución geográfica de la cartera no es trabajo
    # contable, así que el token del contador no habilita esta capability.
    roles = set(get_contract("pacientes.pacientes_por_ciudad_chile").roles)
    assert roles == {"analista_financiero", "gerente_finanzas", "ai_agent"}
    assert "contador" not in roles


def test_rollos_del_registry_cuadran_con_los_tokens_de_env():
    # Si se agrega un token a .env para un rol que ninguna capability declara, o
    # al revés, este test lo señala en vez de dejarlo pasar silencioso.
    roles_de_tokens = set(settings.token_roles.values())
    roles_de_contratos = set().union(*(set(c.roles) for c in all_contracts()))
    assert roles_de_contratos <= KNOWN_ROLES
    assert roles_de_tokens <= KNOWN_ROLES, f"token con rol no declarado: {roles_de_tokens - KNOWN_ROLES}"


# --------------------------------------------------------------------------- #
# Lo que el agente ve realmente (list_tools)
# --------------------------------------------------------------------------- #


def test_list_tools_expone_todas_las_capabilities(tools):
    # Antes comparaba contra 7, un número mágico. Contra el registro no puede
    # desincronizarse: añadir una capability exige que la tool esté publicada.
    assert len(tools) == len(CAPABILITIES)
    assert {t.name for t in tools} == set(contracts_by_name())


@pytest.mark.parametrize("cid", sorted(CAPABILITIES))
def test_list_tools_coincide_con_el_contrato(cid, tools):
    c = get_contract(cid)
    t = next(t for t in tools if t.name == c.name)

    assert t.description == c.mcp_description
    assert t.annotations.title == c.title
    assert t.annotations.readOnlyHint == c.annotations["readOnlyHint"]
    assert t.annotations.destructiveHint == c.annotations["destructiveHint"]
    assert t.annotations.idempotentHint == c.annotations["idempotentHint"]
    assert t.annotations.openWorldHint == c.annotations["openWorldHint"]


@pytest.mark.parametrize("cid", CON_FECHA)
def test_input_schema_pide_fecha_y_tiene_pista_de_formato(cid, tools):
    c = get_contract(cid)
    t = next(t for t in tools if t.name == c.name)
    props = t.inputSchema.get("properties", {})

    assert "fecha" in props
    assert props["fecha"]["description"]
    assert "YYYY-MM-DD" in props["fecha"]["description"]
    assert "fecha" in t.inputSchema["required"]


@pytest.mark.parametrize("cid", SIN_ARGUMENTOS)
def test_input_schema_de_las_sin_argumentos_esta_vacio(cid, tools):
    # El censo de pacientes no admite filtros: un schema con cualquier propiedad
    # prometería un parámetro que la consulta no usa.
    c = get_contract(cid)
    t = next(t for t in tools if t.name == c.name)
    assert t.inputSchema.get("properties", {}) == {}
    assert not t.inputSchema.get("required", [])


def test_solo_tarjeta_tiene_origen_opcional(tools):
    t = next(t for t in tools if t.name == "consultar_ingresos_por_tipo_tarjeta")
    props = t.inputSchema["properties"]
    assert "origen" in props
    assert "origen" not in t.inputSchema["required"]
    assert "CAJA" in props["origen"]["description"]


def test_ninguna_tool_publica_nombres_internos(tools):
    # El agente no debe ver innards de infraestructura ni datos crudos de la BD.
    for t in tools:
        blob = t.description + str(t.inputSchema)
        for prohibido in (
            "INTERNAL",
            "404",
            "Q1_SQL",
            "dent_ciclo",
            "bat_deuda",
            "COD_USUARIO",
            # El censo de pacientes se apoya en estas columnas/tablas; ninguna
            # debe colarse en la descripción que ve el agente.
            "PAC_CODIGO",
            "COD_PERSONA",
            "NOM_CIU",
            "COD_CIU",
            "IND_ESTADO",
            "DENT.DIRECCIONES",
            "DENT.CIUDADES",
        ):
            assert prohibido not in blob, f"{t.name} filtra {prohibido!r}"