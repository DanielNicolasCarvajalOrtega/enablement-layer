import inspect

import pytest
from pydantic import ValidationError as PydanticValidationError

from application.errors import NotFoundError
from application.pacientes.models import ConsultarPacientesPorCiudadChileInput
from application.pacientes.ports import PacientePorCiudadRow, PacientesPort
from application.pacientes.service import PacientesService


class FakeRepo(PacientesPort):
    def __init__(self, rows=None):
        self.rows = rows or []
        self.llamadas = 0

    def pacientes_por_ciudad_chile(self) -> list[PacientePorCiudadRow]:
        self.llamadas += 1
        return self.rows


def _svc(**kwargs) -> PacientesService:
    return PacientesService(FakeRepo(**kwargs))


# --------------------------------------------------------------------------- #
# ENC.PACIENTES_POR_CIUDAD · pacientes por ciudad
# --------------------------------------------------------------------------- #


def test_mapea_filas_totales_y_base():
    svc = _svc(rows=[
        PacientePorCiudadRow("SANTIAGO", 2307),
        PacientePorCiudadRow("PENAFLOR", 26),
    ])
    out = svc.consultar_pacientes_por_ciudad_chile()

    assert [i.ciudad for i in out.items] == ["SANTIAGO", "PENAFLOR"]
    assert out.items[0].cantidad_pacientes == 2307
    assert out.total_pacientes == 2333
    assert out.cantidad_ciudades == 2
    # `base` viaja en el payload: el consumidor no debería tener que recordar que
    # esto no son pacientes activos.
    assert out.base == "pacientes_con_direccion_vigente"


def test_conserva_el_orden_del_sql():
    # El SQL ya ordena por cantidad desc y nombre asc, que es un orden total. La
    # capa no reordena: un segundo sort en Python dejaría el contrato dependiendo
    # del NLS_SORT de Oracle en vez del texto original.
    svc = _svc(rows=[
        PacientePorCiudadRow("SANTIAGO", 2307),
        PacientePorCiudadRow("PENAFLOR", 26),
        PacientePorCiudadRow("BUIN", 16),
    ])
    out = svc.consultar_pacientes_por_ciudad_chile()
    assert [i.ciudad for i in out.items] == ["SANTIAGO", "PENAFLOR", "BUIN"]


def test_no_reordena_una_entrada_desordenada():
    # Si algún día el repository devolviera las filas sin ordenar, esta prueba
    # falla en vez de dejar que la capa "arregle" el orden por su cuenta.
    svc = _svc(rows=[
        PacientePorCiudadRow("BUIN", 16),
        PacientePorCiudadRow("SANTIAGO", 2307),
    ])
    out = svc.consultar_pacientes_por_ciudad_chile()
    assert [i.ciudad for i in out.items] == ["BUIN", "SANTIAGO"]


def test_sin_datos_es_nodata():
    with pytest.raises(NotFoundError) as exc:
        _svc(rows=[]).consultar_pacientes_por_ciudad_chile()
    assert exc.value.error_code == "NO_DATA"


def test_una_sola_consulta_al_repo():
    repo = FakeRepo(rows=[PacientePorCiudadRow("SANTIAGO", 1)])
    PacientesService(repo).consultar_pacientes_por_ciudad_chile()
    assert repo.llamadas == 1


def test_el_service_no_acepta_argumentos():
    # Guarda de contrato: si alguien agrega un filtro (una ciudad, un periodo),
    # esta prueba falla y obliga a revisar la ficha y el catálogo antes de publicar
    # un alcance que el texto original no autoriza.
    params = inspect.signature(PacientesService.consultar_pacientes_por_ciudad_chile).parameters
    assert [p for p in params if p != "self"] == []


def test_el_contrato_de_entrada_rechaza_cualquier_argumento():
    # El schema MCP sale de la firma de la tool, no de este modelo; el modelo fija
    # que esta capacidad no tiene entradas y que no se ignoran en silencio.
    with pytest.raises(PydanticValidationError):
        ConsultarPacientesPorCiudadChileInput(ciudad="SANTIAGO")
    assert ConsultarPacientesPorCiudadChileInput().model_dump() == {}


def test_conserva_nombres_recortados_del_maestro():
    # 'SAN JOSE DE MA' es San José de Maipo. La capa no corrige ni expande el
    # nombre: el texto original agrupa por NOM_CIU y eso es lo que se devuelve.
    svc = _svc(rows=[PacientePorCiudadRow("SAN JOSE DE MA", 10)])
    out = svc.consultar_pacientes_por_ciudad_chile()
    assert out.items[0].ciudad == "SAN JOSE DE MA"


def test_una_ciudad_con_un_paciente_no_se_oculta():
    # No hay umbral mínimo (el legacy de pacientes activos usaba HAVING >= 50).
    # Ocultar ciudades chicas sería inventar un filtro que el texto no pide.
    svc = _svc(rows=[PacientePorCiudadRow("TUCAPEL", 1)])
    out = svc.consultar_pacientes_por_ciudad_chile()
    assert out.cantidad_ciudades == 1
    assert out.items[0].cantidad_pacientes == 1
