from pydantic import ValidationError as PydanticValidationError

from application.errors import NotFoundError, ValidationError
from application.pacientes.models import (
    ConsultarPacientesPorCiudadChileInput,
    ConsultarPacientesPorCiudadChileOutput,
    PacientePorCiudadItem,
)
from application.pacientes.ports import PacientesPort

BASE = "pacientes_con_direccion_vigente"


class PacientesService:
    def __init__(self, repo: PacientesPort):
        self.repo = repo

    def consultar_pacientes_por_ciudad_chile(self) -> ConsultarPacientesPorCiudadChileOutput:
        # La consulta no tiene filtros: no hay fecha que validar ni que el legacy
        # conserve un default roto (V2 §19 h4). El contrato vacío se valida igual
        # para que el schema salga del modelo y cualquier argumento futuro sea un
        # error explícito.
        try:
            ConsultarPacientesPorCiudadChileInput()
        except PydanticValidationError as exc:
            raise ValidationError("Esta consulta no recibe parámetros.") from exc

        rows = self.repo.pacientes_por_ciudad_chile()
        if not rows:
            raise NotFoundError(
                "No hay pacientes con dirección vigente en ninguna ciudad. "
                "Resultado válido, no es un fallo."
            )

        # El ORDER BY del SQL (cantidad desc, nombre asc) ya es un orden total:
        # el nombre de la ciudad es único dentro del grupo. La capa no reordena,
        # porque hacerlo sería arriesgar que un nombre repetido cambie de posición.
        items = [
            PacientePorCiudadItem(ciudad=r.ciudad, cantidad_pacientes=r.cantidad_pacientes)
            for r in rows
        ]
        return ConsultarPacientesPorCiudadChileOutput(
            items=items,
            total_pacientes=sum(i.cantidad_pacientes for i in items),
            cantidad_ciudades=len(items),
            base=BASE,
        )
