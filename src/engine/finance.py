from src.types.project_types import MonthlyCashflow


def calculate_npv(cashflow: list[MonthlyCashflow], rate: float) -> float:
    npv = 0.0
    for i, m in enumerate(cashflow):
        npv += m.net / (1 + rate) ** (i + 1)
    return npv


def calculate_irr(cashflow: list[MonthlyCashflow]) -> float:
    rate = 0.1

    for _ in range(100):
        npv = 0.0
        derivative = 0.0

        try:
            for t, m in enumerate(cashflow):
                cf = m.net
                discount = (1 + rate) ** (t + 1)
                npv += cf / discount
                derivative -= (t + 1) * cf / (discount * (1 + rate))
        except (OverflowError, ZeroDivisionError):
            break

        if derivative == 0:
            break

        new_rate = rate - npv / derivative

        # Clamp to prevent divergence
        new_rate = max(-0.9999, min(new_rate, 1e6))

        if abs(new_rate - rate) < 1e-6:
            return new_rate

        rate = new_rate

    return rate
