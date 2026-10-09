"""Composition root.

Único lugar donde se instancian los adapters concretos. Los adaptadores REST y
MCP comparten la MISMA instancia del service: no debe haber dos objetos
distintos, aunque hoy el service sea stateless (cambiarlo a caching o a un
contador de llamadas haría que divergieran en silencio).
"""

from application.contabilidad.service import ContabilidadService
from application.pacientes.service import PacientesService
from infrastructure.oracle.contabilidad_repository import ContabilidadRepository
from infrastructure.oracle.pacientes_repository import PacientesRepository

contabilidad_repository = ContabilidadRepository()
contabilidad_service = ContabilidadService(contabilidad_repository)

pacientes_repository = PacientesRepository()
pacientes_service = PacientesService(pacientes_repository)