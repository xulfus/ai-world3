"""Time integration wrapper that produces a DataFrame of simulation results."""

import pandas as pd

from ai_world3.model import AIWorldModel


class Simulator:
    """Run an AIWorldModel over time and collect results as a DataFrame."""

    def __init__(self, model: AIWorldModel):
        self.model = model

    def run(self, t_end: float = 100.0, dt: float = 0.1) -> pd.DataFrame:
        self.model.reset()
        records = []
        while self.model.time < t_end:
            state = self.model.step(dt)
            records.append(state)
        return pd.DataFrame(records)
