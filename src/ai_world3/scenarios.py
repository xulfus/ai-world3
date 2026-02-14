"""Preset scenario configurations.

Each scenario is defined as overrides to AIWorldModel defaults.
Parameters are grouped into:
  - Policy levers: what governments can control (thresholds, rates, spending)
  - Technology paths: exogenous assumptions (automation pace, emissions, resources)
"""

import math


def get_laissez_faire_config() -> dict:
    """No policy intervention. Market-only job creation, no emergency tax trigger."""
    return {
        # Policy: hands-off
        "stability_threshold": 0.0,   # no emergency tax trigger
        "retrain_rate": 0.005,        # minimal government retraining
        "job_creation_rate": 0.015,   # slightly below default (less active labor policy)
    }


def get_nordic_ai_config() -> dict:
    """Strong welfare state with aggressive early intervention and active labor policy."""
    return {
        # Policy: aggressive social safety net
        "stability_threshold": 0.85,  # triggers early when stability dips even slightly
        "retrain_rate": 0.05,         # heavy investment in retraining
        "retrain_throughput": 0.25,   # efficient Nordic retraining institutions
        "job_creation_rate": 0.03,    # active labor market programs
        # Technology: slightly cleaner (Nordic emphasis on green tech)
        "emission_rate": 0.0006,
        "absorption_capacity": 0.014,
    }


def get_singularity_config() -> dict:
    """Exponentially accelerating automation. Policy responds but can't keep pace."""
    return {
        # Policy: standard trigger, high retraining (desperate response)
        "stability_threshold": 0.70,
        "retrain_rate": 0.04,
        "retrain_throughput": 0.10,   # systems overwhelmed by pace of change
        # Technology: exponential automation, dirtier
        "automation_speed": lambda t, K_ai: 0.05 * math.exp(0.03 * t),
        "emission_rate": 0.0012,
        "absorption_capacity": 0.010,
    }


def get_green_transition_config() -> dict:
    """Clean technology path with high emission improvement and resource efficiency.

    Unlike the previous version, this does NOT use extreme fixed emission_rate values.
    Instead, it relies on the dynamic emission_improvement_rate and resource_efficiency_rate
    mechanisms to achieve sustainability through technology learning curves.
    """
    return {
        # Policy: moderately strong
        "stability_threshold": 0.80,
        "retrain_rate": 0.04,
        "job_creation_rate": 0.025,
        # Technology: clean, efficient, faster depreciation (tech turnover)
        "emission_improvement_rate": 0.01,   # 10x default — aggressive clean tech
        "resource_efficiency_rate": 0.01,     # 10x default — circular economy
        "depreciation": 0.06,                 # faster tech turnover
        "green_investment_factor": 1.5,        # strong env investment coupling
    }


def get_extraction_config() -> dict:
    """Maximum resource exploitation. No policy response, no efficiency improvement."""
    return {
        # Policy: none
        "stability_threshold": 0.0,
        "retrain_rate": 0.005,
        # Technology: dirty, resource-intensive, no improvement
        "resource_use_rate": 0.15,
        "resource_scarcity_factor": 8.0,
        "emission_rate": 0.002,
        "absorption_capacity": 0.006,
        "emission_improvement_rate": 0.0,    # no clean tech development
        "resource_efficiency_rate": 0.0,      # no efficiency improvement
    }


SCENARIOS = {
    "laissez-faire": get_laissez_faire_config,
    "nordic": get_nordic_ai_config,
    "singularity": get_singularity_config,
    "green-transition": get_green_transition_config,
    "extraction": get_extraction_config,
}
