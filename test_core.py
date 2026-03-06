import unittest

from src.types.project_types import (
    ProjectInput,
    PhysicalInput,
    LandInput,
    OperationalInput,
    SalesInput,
    PaymentPlanInput,
    MensaisInput,
)
from src.engine.core import calculate_core
from src.engine.cashflow import generate_cashflow
from src.engine.finance import calculate_irr, calculate_npv
from src.engine.project import calculate_project
from src.engine.land_residual import calculate_residual_land_value


def make_sample_project() -> ProjectInput:
    return ProjectInput(
        physical=PhysicalInput(
            land_area=5000,
            ca=2.0,
            efficiency_rate=0.85,
            area_per_unit=70.0,
            ticket_medio=500_000,
        ),
        land=LandInput(
            acquisition_type="DINHEIRO",
            land_value=5_000_000,
        ),
        operational=OperationalInput(
            cost_per_m2=2500,
            prazo_total=48,
            prazo_obra=36,
            prazo_vendas=24,
            tma=0.012,  # ~1.2% a.m.
        ),
        sales=SalesInput(mode="PROFILE", profile="BASE"),
        payment_plan=PaymentPlanInput(
            entrada=0.20,
            chaves=0.30,
            mensais=MensaisInput(percentual=0.50, meses=24),
        ),
    )


class TestCore(unittest.TestCase):
    def test_calculate_core(self):
        project = make_sample_project()
        core = calculate_core(project)

        self.assertEqual(core.buildable_area, 10_000)
        self.assertEqual(core.units, 121)
        self.assertAlmostEqual(core.vgv, 121 * 500_000)
        self.assertAlmostEqual(core.cost_total, 10_000 * 2500)
        self.assertEqual(core.land_value, 5_000_000)

    def test_cashflow_length(self):
        project = make_sample_project()
        core = calculate_core(project)
        cashflow = generate_cashflow(core, project)

        self.assertEqual(len(cashflow), project.operational.prazo_total)

    def test_metrics(self):
        project = make_sample_project()
        result = calculate_project(project)

        self.assertIn("irr", result["metrics"])
        self.assertIn("npv", result["metrics"])
        self.assertIsInstance(result["metrics"]["irr"], float)
        self.assertIsInstance(result["metrics"]["npv"], float)

    def test_residual_land_value(self):
        project = make_sample_project()
        result = calculate_residual_land_value(project, target_irr=0.2)

        self.assertIsNotNone(result)
        self.assertIn("land_value", result)
        self.assertIn("irr", result)
        self.assertAlmostEqual(result["irr"], 0.2, delta=0.1)


if __name__ == "__main__":
    unittest.main()
