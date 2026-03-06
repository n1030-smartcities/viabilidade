from src.engine.core import calculate_core
from src.engine.cashflow import generate_cashflow
from src.engine.finance import calculate_irr, calculate_npv
from src.types.project_types import ProjectInput


def calculate_project(project: ProjectInput) -> dict:
    core = calculate_core(project)
    cashflow = generate_cashflow(core, project)

    return {
        "core": core,
        "cashflow": cashflow,
        "metrics": {
            "irr": calculate_irr(cashflow),
            "npv": calculate_npv(cashflow, project.operational.tma),
        },
    }
