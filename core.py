import math
from src.types.project_types import ProjectInput, ProjectCore


def calculate_core(input: ProjectInput) -> ProjectCore:
    buildable_area = input.physical.land_area * input.physical.ca
    private_area = buildable_area * input.physical.efficiency_rate
    units = math.floor(private_area / input.physical.area_per_unit)
    vgv = units * input.physical.ticket_medio
    cost_total = buildable_area * input.operational.cost_per_m2

    land_value = 0.0

    if input.land.acquisition_type == "DINHEIRO":
        land_value = input.land.land_value or 0.0

    elif input.land.acquisition_type == "PERMUTA_FINANCEIRA":
        land_value = vgv * (input.land.permuta_percent or 0.0)

    elif input.land.acquisition_type == "PERMUTA_FISICA":
        permuta_units = units * (input.land.permuta_percent or 0.0)
        land_value = permuta_units * input.physical.ticket_medio

    return ProjectCore(
        buildable_area=buildable_area,
        units=units,
        vgv=vgv,
        cost_total=cost_total,
        land_value=land_value,
    )
