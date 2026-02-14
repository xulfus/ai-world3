"""Matplotlib dashboards for simulation results and sensitivity analysis."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_simulation(
    df: pd.DataFrame,
    title: str = "AI-World3 Simulation",
    stability_threshold: float = 0.7,
) -> plt.Figure:
    """3×3 dashboard of the main simulation variables."""
    fig, axes = plt.subplots(3, 3, figsize=(18, 12))
    fig.suptitle(title, fontsize=14)

    t = df["time"]

    ax = axes[0, 0]
    ax.plot(t, df["K_ai"])
    ax.set_title("AI Capital")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("K_ai")

    ax = axes[0, 1]
    ax.plot(t, df["unemployment_rate"])
    ax.set_title("Unemployment Rate")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Rate")

    ax = axes[0, 2]
    ax.plot(t, df["Stability"])
    if stability_threshold > 0:
        ax.axhline(y=stability_threshold, color="r", linestyle="--", alpha=0.7, label="Threshold")
        ax.legend()
    ax.set_title("Social Stability")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Stability")
    ax.set_ylim(-0.05, 1.05)

    ax = axes[1, 0]
    ax.plot(t, df["Public_Pool"])
    ax.set_title("Public Pool (UBI/Retraining)")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Public_Pool")

    ax = axes[1, 1]
    ax.plot(t, df["tax_rate"])
    ax.set_title("Tax Rate")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Tax Rate")

    ax = axes[1, 2]
    ax.plot(t, df["output"])
    ax.set_title("Economic Output")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Output")

    ax = axes[2, 0]
    ax.plot(t, df["Environment"], color="green")
    ax.axhline(y=0.2, color="r", linestyle="--", alpha=0.7, label="Collapse threshold")
    ax.legend()
    ax.set_title("Environment Quality")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Environment")
    ax.set_ylim(-0.05, 1.05)

    ax = axes[2, 1]
    ax.plot(t, df["Resources"], color="brown")
    ax.axhline(y=0, color="r", linestyle="--", alpha=0.7)
    ax.set_title("Resource Stock")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Resources")

    ax = axes[2, 2]
    ax.plot(t, df["resource_cost_multiplier"], color="orange")
    ax.axhline(y=1.0, color="gray", linestyle="--", alpha=0.7, label="Baseline")
    ax.legend()
    ax.set_title("Resource Cost Multiplier")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Cost Multiplier")

    fig.tight_layout()
    return fig


def plot_tornado(
    corr_df: pd.DataFrame,
    metric_name: str = "final_stability",
    title: str | None = None,
) -> plt.Figure:
    """Horizontal bar chart of Spearman rank correlations (tornado diagram)."""
    fig, ax = plt.subplots(figsize=(10, max(4, len(corr_df) * 0.5)))

    colors = ["#e74c3c" if c < 0 else "#2ecc71" for c in corr_df["correlation"]]
    ax.barh(corr_df["parameter"], corr_df["correlation"], color=colors)
    ax.set_xlabel(f"Spearman correlation with {metric_name}")
    ax.set_title(title or f"Parameter sensitivity: {metric_name}")
    ax.axvline(x=0, color="black", linewidth=0.8)

    fig.tight_layout()
    return fig


def plot_oat_sweep(
    sweep_df: pd.DataFrame,
    metric: str = "final_stability",
    title: str | None = None,
) -> plt.Figure:
    """Grid of OAT sweep results, one subplot per parameter."""
    params = sweep_df["param"].unique()
    n = len(params)
    cols = min(3, n)
    rows = (n + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 4 * rows))
    if n == 1:
        axes = np.array([axes])
    axes = axes.flatten()

    for i, param in enumerate(params):
        subset = sweep_df[sweep_df["param"] == param]
        axes[i].plot(subset["value"], subset[metric], "o-")
        axes[i].set_xlabel(param)
        axes[i].set_ylabel(metric)
        axes[i].set_title(param)

    # Hide unused axes
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle(title or f"One-at-a-time sensitivity: {metric}", fontsize=13)
    fig.tight_layout()
    return fig


def save_plot(fig: plt.Figure, path: str):
    fig.savefig(path, dpi=150, bbox_inches="tight")


def show_plot(fig: plt.Figure):
    plt.show()
