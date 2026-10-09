from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ConsultarPacientesPorCiudadChileInput(BaseModel):
    """Contrato de entrada vacío: la consulta no admite ningún parámetro.

    Se declara igual que en las demás capabilities para que el schema MCP y el de
    OpenAPI salgan de un modelo, no de una firma suelta. `extra="forbid"` deja
    explícito que cualquier argumento es un error y no un argumento ignorado.
    """

    model_config = ConfigDict(extra="forbid")


class PacientePorCiudadItem(BaseModel):
    ciudad: str = Field(
        ...,
        description=(
            "Nombre de la ciudad tal como lo guarda el maestro, que lo almacena "
            "recortado (ej. 'SAN JOSE DE MA' es San José de Maipo)."
        ),
    )
    cantidad_pacientes: int = Field(
        ...,
        description="Pacientes distintos con al menos una dirección vigente en esa ciudad.",
    )


class ConsultarPacientesPorCiudadChileOutput(BaseModel):
    items: list[PacientePorCiudadItem] = Field(
        ...,
        description=(
            "Una fila por ciudad con pacientes, de mayor a menor y con el nombre de la "
            "ciudad como desempate. Las ciudades sin pacientes no aparecen."
        ),
    )
    total_pacientes: int = Field(
        ...,
        description=(
            "Suma de las cantidades por ciudad, calculada por la capa. Puede superar la "
            "cantidad de pacientes distintos si alguno tuviera direcciones vigentes en "
            "más de una ciudad (en QA no ocurre)."
        ),
    )
    cantidad_ciudades: int = Field(
        ..., description="Cuántas ciudades tienen al menos un paciente con dirección vigente."
    )
    base: Literal["pacientes_con_direccion_vigente"] = Field(
        ...,
        description=(
            "Fija en el payload de qué universo habla el resultado: pacientes con "
            "dirección vigente, NO pacientes activos."
        ),
    )
