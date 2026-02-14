"""Tests for the Simulator wrapper."""

import pandas as pd

from ai_world3.model import AIWorldModel
from ai_world3.simulator import Simulator


class TestSimulator:
    def test_returns_dataframe(self):
        sim = Simulator(AIWorldModel())
        df = sim.run(t_end=10, dt=1.0)
        assert isinstance(df, pd.DataFrame)

    def test_correct_time_column(self):
        sim = Simulator(AIWorldModel())
        df = sim.run(t_end=10, dt=1.0)
        assert "time" in df.columns
        assert df.iloc[0]["time"] == 1.0
        assert df.iloc[-1]["time"] == 10.0

    def test_dt_affects_row_count(self):
        sim = Simulator(AIWorldModel())
        df1 = sim.run(t_end=10, dt=1.0)
        df2 = sim.run(t_end=10, dt=0.5)
        assert len(df1) == 10
        assert len(df2) == 20

    def test_has_all_columns(self):
        sim = Simulator(AIWorldModel())
        df = sim.run(t_end=5, dt=1.0)
        expected = {
            "time", "K_ai", "Labor_U", "unemployment_rate", "labor_force",
            "Stability", "Public_Pool", "tax_rate", "output",
            "Environment", "Resources", "resource_cost_multiplier",
        }
        assert set(df.columns) == expected
