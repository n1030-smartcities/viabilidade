from src.types.project_types import ProjectCore, ProjectInput


def generate_sales_curve(core: ProjectCore, project: ProjectInput) -> list[float]:
    if project.sales.mode == "CUSTOM":
        return project.sales.custom_curve or []

    months = project.operational.prazo_vendas
    units_per_month = core.units / months
    return [units_per_month] * months
