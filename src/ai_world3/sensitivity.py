"""Sensitivity analysis tools: one-at-a-time sweeps and Latin Hypercube Sampling."""

from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd

from ai_world3.model import AIWorldModel
from ai_world3.simulator import Simulator


# ── Metric extractors ──────────────────────────────────────────────────────

def _extract_metrics(df: pd.DataFrame) -> dict:
    """Compute summary metrics from a simulation run."""
    metrics: dict = {}

    # Final-state metrics
    last = df.iloc[-1]
    metrics["final_stability"] = last["Stability"]
    metrics["final_K_ai"] = last["K_ai"]
    metrics["final_output"] = last["output"]
    metrics["final_environment"] = last["Environment"]
    metrics["final_resources"] = last["Resources"]
    metrics["final_unemployment_rate"] = last["unemployment_rate"]
    metrics["final_tax_rate"] = last["tax_rate"]

    # Extrema
    metrics["min_stability"] = df["Stability"].min()
    metrics["max_unemployment_rate"] = df["unemployment_rate"].max()
    metrics["peak_K_ai"] = df["K_ai"].max()
    metrics["min_environment"] = df["Environment"].min()

    # Collapse times (first time a variable crosses a critical threshold)
    stability_collapse = df[df["Stability"] <= 0.01]
    metrics["stability_collapse_year"] = (
        float(stability_collapse.iloc[0]["time"]) if len(stability_collapse) > 0 else float("inf")
    )
    env_collapse = df[df["Environment"] <= 0.1]
    metrics["env_collapse_year"] = (
        float(env_collapse.iloc[0]["time"]) if len(env_collapse) > 0 else float("inf")
    )
    resource_depletion = df[df["Resources"] <= 1.0]
    metrics["resource_depletion_year"] = (
        float(resource_depletion.iloc[0]["time"]) if len(resource_depletion) > 0 else float("inf")
    )

    return metrics


# ── One-at-a-time sweeps ────────────────────────────────────────────────────

def oat_sweep(
    base_config: dict,
    param_name: str,
    values: list[float],
    t_end: float = 100.0,
    dt: float = 0.5,
) -> pd.DataFrame:
    """Sweep a single parameter while holding all others at baseline.

    Returns a DataFrame with one row per value, containing all metrics.
    """
    rows = []
    for val in values:
        config = base_config.copy()
        config[param_name] = val
        model = AIWorldModel(**config)
        sim = Simulator(model)
        df = sim.run(t_end=t_end, dt=dt)
        metrics = _extract_metrics(df)
        metrics["param"] = param_name
        metrics["value"] = val
        rows.append(metrics)
    return pd.DataFrame(rows)


def multi_oat_sweep(
    base_config: dict,
    param_ranges: dict[str, list[float]],
    t_end: float = 100.0,
    dt: float = 0.5,
) -> pd.DataFrame:
    """Run OAT sweeps for multiple parameters. Returns combined DataFrame."""
    frames = []
    for param_name, values in param_ranges.items():
        frame = oat_sweep(base_config, param_name, values, t_end=t_end, dt=dt)
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


# ── Latin Hypercube Sampling ────────────────────────────────────────────────

def lhs_sample(
    base_config: dict,
    param_ranges: dict[str, tuple[float, float]],
    n_samples: int = 50,
    t_end: float = 100.0,
    dt: float = 0.5,
    seed: int = 42,
) -> pd.DataFrame:
    """Latin Hypercube Sampling of the parameter space.

    Args:
        base_config: Baseline parameters (non-swept params stay fixed).
        param_ranges: {param_name: (min_val, max_val)} for each swept parameter.
        n_samples: Number of samples to draw.
        t_end: Simulation horizon.
        dt: Time step.
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with one row per sample, containing parameter values + all metrics.
    """
    from scipy.stats.qmc import LatinHypercube

    param_names = list(param_ranges.keys())
    n_dims = len(param_names)

    sampler = LatinHypercube(d=n_dims, seed=seed)
    unit_samples = sampler.random(n=n_samples)  # shape (n_samples, n_dims) in [0,1]

    rows = []
    for i in range(n_samples):
        config = base_config.copy()
        sample_params = {}
        for j, param in enumerate(param_names):
            lo, hi = param_ranges[param]
            val = lo + unit_samples[i, j] * (hi - lo)
            config[param] = val
            sample_params[param] = val

        model = AIWorldModel(**config)
        sim = Simulator(model)
        df = sim.run(t_end=t_end, dt=dt)
        metrics = _extract_metrics(df)
        metrics.update(sample_params)
        metrics["sample_id"] = i
        rows.append(metrics)

    return pd.DataFrame(rows)


def rank_correlations(
    lhs_df: pd.DataFrame,
    param_names: list[str],
    metric: str = "final_stability",
) -> pd.DataFrame:
    """Compute Spearman rank correlations between parameters and a metric.

    Returns a DataFrame sorted by absolute correlation (for tornado diagrams).
    """
    from scipy.stats import spearmanr

    rows = []
    metric_values = lhs_df[metric].values
    for param in param_names:
        param_values = lhs_df[param].values
        corr, pvalue = spearmanr(param_values, metric_values)
        rows.append({"parameter": param, "correlation": corr, "abs_correlation": abs(corr), "p_value": pvalue})

    df = pd.DataFrame(rows).sort_values("abs_correlation", ascending=False).reset_index(drop=True)
    return df


# ── Default parameter ranges for sensitivity analysis ───────────────────────

DEFAULT_OAT_RANGES: dict[str, list[float]] = {
    "automation_speed": [0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10],
    "churn_rate": [0.0, 0.005, 0.01, 0.015, 0.02, 0.03],
    "retrain_rate": [0.0, 0.01, 0.02, 0.03, 0.05, 0.08],
    "job_creation_rate": [0.005, 0.01, 0.015, 0.02, 0.03, 0.04],
    "stability_threshold": [0.0, 0.3, 0.5, 0.7, 0.85, 0.95],
    "emission_rate": [0.0002, 0.0005, 0.0008, 0.0012, 0.002],
    "resource_use_rate": [0.01, 0.03, 0.05, 0.10, 0.15],
}

DEFAULT_LHS_RANGES: dict[str, tuple[float, float]] = {
    "automation_speed": (0.02, 0.10),
    "churn_rate": (0.0, 0.03),
    "retrain_rate": (0.0, 0.08),
    "job_creation_rate": (0.005, 0.04),
    "job_creation_saturation": (20.0, 200.0),
    "mismatch_fraction": (0.0, 0.8),
    "stability_threshold": (0.0, 0.95),
    "emission_rate": (0.0002, 0.002),
    "resource_use_rate": (0.01, 0.15),
    "emission_improvement_rate": (0.0, 0.01),
    "resource_efficiency_rate": (0.0, 0.01),
}
