from fastapi import APIRouter, Depends

from application.pacientes.models import ConsultarPacientesPorCiudadChileOutput
from composition import pacientes_service
from security import require_contract

router = APIRouter(prefix="/api/pacientes", tags=["pacientes"])


@router.get(
    "/pacientes-por-ciudad-chile",
    response_model=ConsultarPacientesPorCiudadChileOutput,
    summary="Pacientes por ciudad (Chile)",
)
def consultar_pacientes_por_ciudad_chile(
    identity: dict = Depends(require_contract("pacientes.pacientes_por_ciudad_chile")),
):
    """Pacientes con al menos una dirección vigente, agrupados por ciudad.

    No recibe parámetros y NO cuenta pacientes activos: no filtra por el estado de
    la ficha. `base` viaja en el payload para que el consumidor no tenga que
    recordar la semántica.
    """
    return pacientes_service.consultar_pacientes_por_ciudad_chile()
