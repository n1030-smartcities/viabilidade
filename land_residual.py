import copy

from src.engine.core import calculate_core
from src.engine.cashflow import generate_cashflow
from src.engine.finance import calculate_irr
from src.types.project_types import ProjectInput


def calculate_residual_land_value(
    project: ProjectInput, target_irr: float = 0.2
) -> dict | None:
    low = 0.0
    high = project.physical.land_area * 5000
    best = None

    for _ in range(50):
        mid = (low + high) / 2

        scenario = copy.deepcopy(project)
        scenario.land.land_value = mid
        scenario.land.acquisition_type = "DINHEIRO"

        core = calculate_core(scenario)
        cashflow = generate_cashflow(core, scenario)
        irr = calculate_irr(cashflow)

        if best is None or abs(irr - target_irr) < abs(best["irr"] - target_irr):
            best = {
                "land_value": mid,
                "irr": irr,
                "vgv": core.vgv,
                "units": core.units,
            }

        if irr > target_irr:
            low = mid
        else:
            high = mid

    return best
