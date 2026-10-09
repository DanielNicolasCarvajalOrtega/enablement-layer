from abc import ABC, abstractmethod
from typing import NamedTuple


class PacientePorCiudadRow(NamedTuple):
    """Fila (ciudad, cantidad) de la consulta de pacientes por ciudad.

    ``ciudad`` es el NOMBRO del maestro, no el código: el SQL agrupa por nombre, así
    que el código de ciudad no viaja al contrato.
    """

    ciudad: str
    cantidad_pacientes: int


class PacientesPort(ABC):
    """Puerto de persistencia del bloque Pacientes (V2 R15)."""

    @abstractmethod
    def pacientes_por_ciudad_chile(self) -> list[PacientePorCiudadRow]:
        """Pacientes con dirección vigente agrupados por ciudad. Sin parámetros."""
