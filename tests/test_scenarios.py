"""Integration tests for all scenarios."""

import pytest
from ai_world3.model import AIWorldModel
from ai_world3.scenarios import (
    SCENARIOS,
    get_laissez_faire_config,
    get_nordic_ai_config,
    get_singularity_config,
    get_green_transition_config,
    get_extraction_config,
)
from ai_world3.simulator import Simulator


class TestLaissezFaire:
    def test_stability_collapses(self):
        """Without policy intervention, stability should eventually collapse."""
        model = AIWorldModel(**get_laissez_faire_config())
        sim = Simulator(model)
        df = sim.run(t_end=200, dt=1.0)
        min_stability = df["Stability"].min()
        assert min_stability < 0.3, f"Expected collapse, min stability was {min_stability}"


class TestNordicAI:
    def test_stability_sustained(self):
        """Nordic model should maintain reasonable stability over long horizon."""
        model = AIWorldModel(**get_nordic_ai_config())
        sim = Simulator(model)
        df = sim.run(t_end=200, dt=1.0)
        final_stability = df.iloc[-1]["Stability"]
        assert final_stability > 0.3, f"Expected sustained stability, got {final_stability}"

    def test_unemployment_rate_bounded(self):
        """Unemployment rate should stay bounded (not run away in absolute terms)."""
        model = AIWorldModel(**get_nordic_ai_config())
        sim = Simulator(model)
        df = sim.run(t_end=200, dt=1.0)
        max_urate = df["unemployment_rate"].max()
        assert max_urate < 1.0, f"Unemployment rate should stay < 100%, got {max_urate}"


class TestSingularity:
    def test_stability_collapses(self):
        """Exponential automation should overwhelm policy and cause stability collapse."""
        model = AIWorldModel(**get_singularity_config())
        sim = Simulator(model)
        df = sim.run(t_end=100, dt=1.0)
        min_stability = df["Stability"].min()
        assert min_stability < 0.05, f"Expected stability collapse, min was {min_stability}"

    def test_environment_collapses(self):
        """Singularity scenario should also cause environmental collapse."""
        model = AIWorldModel(**get_singularity_config())
        sim = Simulator(model)
        df = sim.run(t_end=100, dt=1.0)
        min_env = df["Environment"].min()
        assert min_env < 0.1, f"Expected env collapse, min was {min_env}"

    def test_elevated_tax_rate(self):
        model = AIWorldModel(**get_singularity_config())
        sim = Simulator(model)
        df = sim.run(t_end=100, dt=1.0)
        assert df["tax_rate"].max() >= 0.40, "Expected elevated tax rate"


class TestGreenTransition:
    def test_environment_sustained(self):
        """Green transition should sustain environment without extreme parameter tuning."""
        model = AIWorldModel(**get_green_transition_config())
        sim = Simulator(model)
        df = sim.run(t_end=150, dt=1.0)
        min_env = df["Environment"].min()
        assert min_env > 0.4, (
            f"Expected sustained environment, min was {min_env:.3f}"
        )

    def test_resources_last(self):
        model = AIWorldModel(**get_green_transition_config())
        sim = Simulator(model)
        df = sim.run(t_end=150, dt=1.0)
        final_resources = df.iloc[-1]["Resources"]
        assert final_resources > 100, (
            f"Expected resources to last, got {final_resources:.1f}"
        )


class TestExtraction:
    def test_environment_collapses(self):
        model = AIWorldModel(**get_extraction_config())
        sim = Simulator(model)
        df = sim.run(t_end=100, dt=1.0)
        final_env = df.iloc[-1]["Environment"]
        assert final_env < 0.3, (
            f"Expected env collapse, got {final_env:.3f}"
        )

    def test_resources_mostly_gone(self):
        model = AIWorldModel(**get_extraction_config())
        sim = Simulator(model)
        df = sim.run(t_end=100, dt=1.0)
        final_resources = df.iloc[-1]["Resources"]
        assert final_resources < 200, (
            f"Expected significant depletion, got {final_resources:.1f}"
        )


class TestAllScenarios:
    @pytest.mark.parametrize("name", list(SCENARIOS.keys()))
    def test_scenario_runs_without_error(self, name):
        config = SCENARIOS[name]()
        model = AIWorldModel(**config)
        sim = Simulator(model)
        df = sim.run(t_end=50, dt=1.0)
        assert len(df) > 0
        assert "Environment" in df.columns
        assert "Resources" in df.columns
        assert "unemployment_rate" in df.columns
        assert "labor_force" in df.columns
