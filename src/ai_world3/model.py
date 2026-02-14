"""Core simulation model following the spec.md ODE system.

Revised model with:
- Hybrid displacement (churn + growth-driven)
- Natural job creation
- Explicit labor force and unemployment rate
- Symmetric stability normalization
- Dynamic emission intensity and resource efficiency
- Stability-linked environmental absorption
"""

from __future__ import annotations

from typing import Callable

import numpy as np


class AIWorldModel:
    """Stock-and-flow model tracking AI capital, unemployment, stability, and public funds."""

    def __init__(
        self,
        # --- State variables (stocks) ---
        K_ai: float = 100.0,
        Labor_U: float = 5.0,
        Stability: float = 1.0,
        Public_Pool: float = 10.0,
        Environment: float = 0.8,
        Resources: float = 1000.0,
        # --- Automation & labor parameters ---
        automation_speed: float | Callable = 0.05,
        churn_rate: float = 0.01,
        job_creation_rate: float = 0.02,
        job_creation_saturation: float = 50.0,
        mismatch_fraction: float = 0.5,
        retrain_rate: float = 0.02,
        retrain_throughput: float = 0.15,
        labor_force_base: float = 100.0,
        labor_force_k_sensitivity: float = 0.5,
        # --- Capital parameters ---
        depreciation: float = 0.03,
        # --- Tax/policy parameters ---
        stability_threshold: float = 0.7,
        base_tax: float = 0.20,
        max_tax: float = 0.70,
        # --- Stability weights ---
        unemployment_stress_weight: float = 0.5,
        tax_stress_weight: float = 0.1,
        public_pool_stabilizer: float = 0.05,
        # --- Environment parameters ---
        emission_rate: float = 0.0008,
        emission_improvement_rate: float = 0.001,
        absorption_capacity: float = 0.012,
        green_investment_factor: float = 0.5,
        env_output_sensitivity: float = 0.5,
        env_stability_sensitivity: float = 0.3,
        # --- Resource parameters ---
        resource_use_rate: float = 0.05,
        resource_efficiency_rate: float = 0.001,
        resource_scarcity_factor: float = 5.0,
    ):
        self._init_params = {
            "K_ai": K_ai,
            "Labor_U": Labor_U,
            "Stability": Stability,
            "Public_Pool": Public_Pool,
            "Environment": Environment,
            "Resources": Resources,
            "automation_speed": automation_speed,
            "churn_rate": churn_rate,
            "job_creation_rate": job_creation_rate,
            "job_creation_saturation": job_creation_saturation,
            "mismatch_fraction": mismatch_fraction,
            "retrain_rate": retrain_rate,
            "retrain_throughput": retrain_throughput,
            "labor_force_base": labor_force_base,
            "labor_force_k_sensitivity": labor_force_k_sensitivity,
            "depreciation": depreciation,
            "stability_threshold": stability_threshold,
            "base_tax": base_tax,
            "max_tax": max_tax,
            "unemployment_stress_weight": unemployment_stress_weight,
            "tax_stress_weight": tax_stress_weight,
            "public_pool_stabilizer": public_pool_stabilizer,
            "emission_rate": emission_rate,
            "emission_improvement_rate": emission_improvement_rate,
            "absorption_capacity": absorption_capacity,
            "green_investment_factor": green_investment_factor,
            "env_output_sensitivity": env_output_sensitivity,
            "env_stability_sensitivity": env_stability_sensitivity,
            "resource_use_rate": resource_use_rate,
            "resource_efficiency_rate": resource_efficiency_rate,
            "resource_scarcity_factor": resource_scarcity_factor,
        }
        self._resource_stock_initial = Resources
        self._apply_params(self._init_params)
        self.time = 0.0
        self._current_tax = self.base_tax
        self._prev_K_ai = K_ai

    def _apply_params(self, params):
        for key, value in params.items():
            setattr(self, key, value)

    def _get_automation_speed(self):
        if callable(self.automation_speed):
            return self.automation_speed(self.time, self.K_ai)
        return self.automation_speed

    def step(self, dt: float = 1.0) -> dict:
        """Advance the model by *dt* and return the current state including derived values."""

        # ── 1. Tax trigger (smooth sigmoid + inertia) ──
        if self.stability_threshold > 0:
            gap = self.stability_threshold - self.Stability
            emergency = 1.0 / (1.0 + np.exp(-2 * gap / self.stability_threshold))
            target_tax = self.base_tax + emergency * (self.max_tax - self.base_tax)
        else:
            target_tax = self.base_tax
        target_tax = min(target_tax, self.max_tax)
        alpha = 1.0 - np.exp(-dt / 2.0)
        self._current_tax += alpha * (target_tax - self._current_tax)
        current_tax = self._current_tax

        # ── 2. Economic output ──
        raw_output = self.K_ai * 0.3

        # 2a. Environment dynamics — dynamic emission intensity
        tech_factor = 1.0 / (1.0 + self.emission_improvement_rate * self.K_ai)
        effective_emission_rate = self.emission_rate * tech_factor
        emissions = effective_emission_rate * raw_output

        # Stability-linked absorption (stable societies invest in environment)
        adjusted_absorption = self.absorption_capacity * (
            1.0 + self.green_investment_factor * self.Stability
        )
        absorption = adjusted_absorption * self.Environment * (1 + self.Environment)

        self.Environment += (absorption - emissions) * dt
        self.Environment = float(np.clip(self.Environment, 0, 1))

        # 2b. Environment -> output penalty
        env_multiplier = 1.0 - self.env_output_sensitivity * (1 - self.Environment) ** 2
        output = raw_output * env_multiplier

        # 2c. Resource depletion — dynamic resource efficiency
        resource_efficiency = 1.0 / (1.0 + self.resource_efficiency_rate * self.K_ai)
        self.Resources -= self.resource_use_rate * self.K_ai * resource_efficiency * dt
        self.Resources = max(self.Resources, 0.0)

        # 2d. Resource scarcity -> cost penalty
        fraction_remaining = self.Resources / self._resource_stock_initial
        resource_cost_multiplier = (
            1.0 + self.resource_scarcity_factor * (1 - fraction_remaining) ** 2
        )
        effective_output = output / resource_cost_multiplier

        # 2e. Tax revenue
        tax_revenue = effective_output * current_tax
        self.Public_Pool += tax_revenue * dt

        # ── 3. Labor dynamics (hybrid displacement) ──
        speed = self._get_automation_speed()

        # Labor force grows with the economy
        labor_force = self.labor_force_base + self.labor_force_k_sensitivity * self.K_ai
        unemployment_rate_prev = self.Labor_U / max(labor_force, 1.0)

        # Growth-driven displacement: only new capital displaces
        dK_ai = self.K_ai - self._prev_K_ai
        growth_displacement = max(dK_ai / max(dt, 1e-9), 0) * speed

        # Churn displacement: ongoing automation of existing roles
        churn_displacement = labor_force * self.churn_rate

        displacement = growth_displacement + churn_displacement

        # Natural job creation: saturating with output, scaled by confidence
        # Michaelis-Menten: linear at small output, saturates at large output
        raw_job_creation = effective_output * self.job_creation_rate * (
            0.5 + 0.5 * self.Stability
        )
        saturation = self.job_creation_saturation / (
            self.job_creation_saturation + effective_output
        )
        # Structural mismatch: harder to fill jobs when many displaced workers
        # come from different sectors (uses start-of-step unemployment)
        mismatch_penalty = max(
            1.0 - self.mismatch_fraction * min(unemployment_rate_prev, 1.0), 0.0
        )
        natural_jobs = raw_job_creation * saturation * mismatch_penalty

        # Government-funded retraining (limited by funding AND institutional throughput)
        reinstatement = min(
            self.Public_Pool * self.retrain_rate,    # funding constraint
            self.Labor_U * self.retrain_throughput,   # capacity: max fraction retrained per year
        )

        self.Labor_U += (displacement - natural_jobs - reinstatement) * dt
        self.Labor_U = max(self.Labor_U, 0.0)

        # Unemployment rate (dimensionless)
        unemployment_rate = self.Labor_U / max(labor_force, 1.0)

        # ── 4. Social stability (symmetrically normalized) ──
        stability_drain = (
            unemployment_rate * self.unemployment_stress_weight
            + (current_tax / self.max_tax) * self.tax_stress_weight
            + self.env_stability_sensitivity * (1 - self.Environment) ** 1.5
        )
        economy_scale = max(self.K_ai, 1.0)
        stability_gain = (self.Public_Pool / economy_scale) * self.public_pool_stabilizer

        self.Stability += (stability_gain - stability_drain) * dt
        self.Stability = float(np.clip(self.Stability, 0, 1))

        # ── 5. Public Pool spending (retraining + UBI) ──
        self.Public_Pool -= (reinstatement + stability_gain) * dt
        self.Public_Pool = max(self.Public_Pool, 0.0)

        # ── 6. Capital re-investment ──
        investment = (effective_output - tax_revenue) * self.Stability
        self.K_ai += (investment - (self.K_ai * self.depreciation)) * dt

        # Track previous K_ai for next step's growth calculation
        self._prev_K_ai = self.K_ai
        self.time += dt

        return {
            "time": self.time,
            "K_ai": self.K_ai,
            "Labor_U": self.Labor_U,
            "unemployment_rate": unemployment_rate,
            "labor_force": labor_force,
            "Stability": self.Stability,
            "Public_Pool": self.Public_Pool,
            "tax_rate": current_tax,
            "output": effective_output,
            "Environment": self.Environment,
            "Resources": self.Resources,
            "resource_cost_multiplier": resource_cost_multiplier,
        }

    def get_state(self) -> dict:
        labor_force = self.labor_force_base + self.labor_force_k_sensitivity * self.K_ai
        return {
            "time": self.time,
            "K_ai": self.K_ai,
            "Labor_U": self.Labor_U,
            "unemployment_rate": self.Labor_U / max(labor_force, 1.0),
            "labor_force": labor_force,
            "Stability": self.Stability,
            "Public_Pool": self.Public_Pool,
            "Environment": self.Environment,
            "Resources": self.Resources,
        }

    def reset(self):
        self._apply_params(self._init_params)
        self._resource_stock_initial = self._init_params["Resources"]
        self.time = 0.0
        self._current_tax = self.base_tax
        self._prev_K_ai = self._init_params["K_ai"]
