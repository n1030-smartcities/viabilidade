from src.types.project_types import PaymentPlanInput


def generate_payment_schedule(
    sale_month: int, sale_value: float, plan: PaymentPlanInput
) -> list[dict]:
    schedule = []

    # Entrada: paid at time of sale
    if plan.entrada > 0:
        schedule.append({"month": sale_month, "value": sale_value * plan.entrada})

    # Mensais: monthly installments during construction
    if plan.mensais and plan.mensais.percentual > 0:
        monthly_value = (sale_value * plan.mensais.percentual) / plan.mensais.meses
        for i in range(plan.mensais.meses):
            schedule.append({"month": sale_month + i + 1, "value": monthly_value})

    # Chaves: paid after monthly period ends
    if plan.chaves > 0:
        chaves_month = sale_month + (plan.mensais.meses if plan.mensais else 0) + 1
        schedule.append({"month": chaves_month, "value": sale_value * plan.chaves})

    return schedule
