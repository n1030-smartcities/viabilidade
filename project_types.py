from dataclasses import dataclass, field
from typing import Literal, Optional


@dataclass
class PhysicalInput:
    land_area: float
    ca: float
    efficiency_rate: float
    area_per_unit: float
    ticket_medio: float


@dataclass
class LandInput:
    acquisition_type: Literal["DINHEIRO", "PERMUTA_FINANCEIRA", "PERMUTA_FISICA"]
    land_value: Optional[float] = None
    permuta_percent: Optional[float] = None


@dataclass
class OperationalInput:
    cost_per_m2: float
    prazo_total: int
    prazo_obra: int
    prazo_vendas: int
    tma: float


@dataclass
class MensaisInput:
    percentual: float
    meses: int


@dataclass
class SalesInput:
    mode: Literal["PROFILE", "CUSTOM"]
    profile: Optional[Literal["CONSERVADOR", "BASE", "AGRESSIVO"]] = None
    custom_curve: Optional[list[float]] = None


@dataclass
class PaymentPlanInput:
    entrada: float
    chaves: float
    mensais: Optional[MensaisInput] = None


@dataclass
class ProjectInput:
    physical: PhysicalInput
    land: LandInput
    operational: OperationalInput
    sales: SalesInput
    payment_plan: PaymentPlanInput


@dataclass
class ProjectCore:
    buildable_area: float
    units: int
    vgv: float
    cost_total: float
    land_value: float


@dataclass
class MonthlyCashflow:
    month: int
    inflow: float
    outflow: float
    net: float
    accumulated: float
