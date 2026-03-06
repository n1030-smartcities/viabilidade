from collections import defaultdict

from src.engine.sales_curve import generate_sales_curve
from src.engine.payment_plan import generate_payment_schedule
from src.types.project_types import MonthlyCashflow, ProjectCore, ProjectInput


def generate_cashflow(
    core: ProjectCore, project: ProjectInput
) -> list[MonthlyCashflow]:
    sales_curve = generate_sales_curve(core, project)
    receipts: dict[int, float] = defaultdict(float)
    price = core.vgv / core.units

    for index, units in enumerate(sales_curve):
        sale_month = index + 1
        sale_value = units * price
        schedule = generate_payment_schedule(sale_month, sale_value, project.payment_plan)

        for p in schedule:
            receipts[p["month"]] += p["value"]

    cashflow: list[MonthlyCashflow] = []
    accumulated = 0.0

    for m in range(1, project.operational.prazo_total + 1):
        inflow = receipts.get(m, 0.0)
        outflow = 0.0

        if m <= project.operational.prazo_obra:
            outflow = core.cost_total / project.operational.prazo_obra

        net = inflow - outflow
        accumulated += net

        cashflow.append(
            MonthlyCashflow(
                month=m,
                inflow=inflow,
                outflow=outflow,
                net=net,
                accumulated=accumulated,
            )
        )

    return cashflow
