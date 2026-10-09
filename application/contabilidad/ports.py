from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import NamedTuple


class IngresoRow(NamedTuple):
    tipo_pago: str
    monto: Decimal


class DeudaRow(NamedTuple):
    """Fila (mes, deuda) de Q3. ``mes`` es el MM del grupo; la etiqueta
    MM-YYYY y el periodo normalizado los arma el service, no el SQL."""

    mes: str
    deuda: Decimal


class TarjetaRow(NamedTuple):
    """Fila de Q10 por canal. ``tipo`` es lo que entrega el SQL del canal:
    crudo en CAJA (CRD1/DEB1) y ya decodificado en TOTEM/WEBPAY."""

    tipo: str
    codigo: str
    cantidad: int
    monto: Decimal


class PrevisionRow(NamedTuple):
    prevision: str
    cantidad: int
    monto: Decimal


class BoletaPorUsuarioRow(NamedTuple):
    apellido: str
    nombre: str
    cantidad: int
    monto: Decimal


class ContabilidadPort(ABC):
    """Puerto de persistencia del bloque Control Contable (V2 R15)."""

    @abstractmethod
    def ingresos_por_tipo_pago(self, fecha: date) -> list[IngresoRow]:
        """Fila (tipo_doc, monto) tal como la entrega la query Q1 (group by NUM_DOCTO)."""

    @abstractmethod
    def deuda_del_mes(self, periodo: str) -> DeudaRow | None:
        """Q3 · un período YYYY-MM. Devuelve None si el mes no tiene filas:
        el legacy OMITE el mes, no lo completa con cero."""

    @abstractmethod
    def ingresos_por_tipo_tarjeta(self, fecha: date, origen: str) -> list[TarjetaRow]:
        """Q10 · un canal (CAJA | TOTEM | WEBPAY). Cada canal tiene su propio SQL."""

    @abstractmethod
    def ingresos_por_tipo_prevision(self, fecha: date) -> list[PrevisionRow]:
        """Q11 · banda horaria del día, agrupado por DOMIDESCRI."""

    @abstractmethod
    def boletas_por_usuario(self, fecha: date) -> list[BoletaPorUsuarioRow]:
        """Q8 · boletas activas del día por USUAPEP/USUNOMC."""

    @abstractmethod
    def boletas_anuladas_por_usuario(self, fecha: date) -> list[BoletaPorUsuarioRow]:
        """Q9 · estados ANU/DEV/NCI. Filtra por FEC_BOL exacto (sin trunc), como el legacy."""