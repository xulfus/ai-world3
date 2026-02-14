"""CLI entry point for AI-World3 simulations."""

import argparse
import json
import sys

from ai_world3.model import AIWorldModel
from ai_world3.scenarios import SCENARIOS
from ai_world3.simulator import Simulator
from ai_world3.visualizer import plot_simulation, save_plot, show_plot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-world3",
        description="AI-World3: Simulate AI automation vs social stability",
    )
    parser.add_argument(
        "scenario",
        choices=list(SCENARIOS.keys()) + ["custom"],
        help="Scenario to run",
    )
    parser.add_argument("--t-end", type=float, default=100.0, help="Simulation end time (years)")
    parser.add_argument("--dt", type=float, default=0.1, help="Time step size")
    parser.add_argument("--output", type=str, help="Save results to CSV file")
    parser.add_argument("--plot", action="store_true", help="Show plot window")
    parser.add_argument("--plot-file", type=str, help="Save plot to file")

    # Custom scenario parameters
    custom = parser.add_argument_group("custom scenario parameters")
    custom.add_argument("--k-ai", type=float, default=100.0)
    custom.add_argument("--labor-u", type=float, default=5.0)
    custom.add_argument("--stability", type=float, default=1.0)
    custom.add_argument("--public-pool", type=float, default=10.0)
    custom.add_argument("--automation-speed", type=float, default=0.05)
    custom.add_argument("--churn-rate", type=float, default=0.01)
    custom.add_argument("--job-creation-rate", type=float, default=0.02)
    custom.add_argument("--retrain-rate", type=float, default=0.02)
    custom.add_argument("--depreciation", type=float, default=0.03)
    custom.add_argument("--stability-threshold", type=float, default=0.7)
    custom.add_argument("--base-tax", type=float, default=0.20)
    custom.add_argument("--max-tax", type=float, default=0.70)

    # Environmental parameters
    env = parser.add_argument_group("environmental parameters")
    env.add_argument("--env-initial", type=float, default=0.8, help="Initial environment quality (0-1)")
    env.add_argument("--env-emission-rate", type=float, default=0.0008, help="Emissions per unit output")
    env.add_argument("--env-emission-improvement", type=float, default=0.001, help="Emission intensity improvement rate")
    env.add_argument("--env-absorption", type=float, default=0.012, help="Base environmental self-cleaning rate")
    env.add_argument("--green-investment-factor", type=float, default=0.5, help="Stability->absorption coupling")
    env.add_argument("--env-output-sensitivity", type=float, default=0.5, help="Output penalty from env degradation")
    env.add_argument("--env-stability-sensitivity", type=float, default=0.3, help="Stability drain from env degradation")
    env.add_argument("--resource-initial", type=float, default=1000.0, help="Initial resource stock")
    env.add_argument("--resource-use-rate", type=float, default=0.05, help="Resource consumption per K_ai unit")
    env.add_argument("--resource-efficiency-rate", type=float, default=0.001, help="Resource efficiency improvement rate")
    env.add_argument("--resource-scarcity-factor", type=float, default=5.0, help="Cost multiplier intensity")

    # Sensitivity analysis
    sens = parser.add_argument_group("sensitivity analysis")
    sens.add_argument("--sensitivity-oat", action="store_true", help="Run one-at-a-time sensitivity sweeps")
    sens.add_argument("--sensitivity-lhs", type=int, default=0, metavar="N", help="Run LHS with N samples")
    sens.add_argument("--sensitivity-output", type=str, help="Save sensitivity results to CSV")
    sens.add_argument("--sensitivity-plot", type=str, help="Save sensitivity plot to file")

    return parser


def print_summary(df):
    final = df.iloc[-1]
    print("\n--- Simulation Summary ---")
    print(f"  Final AI Capital:       {final['K_ai']:.2f}")
    print(f"  Final Unemployment:     {final['Labor_U']:.4f}")
    print(f"  Final Unemployment Rate:{final['unemployment_rate']:.4f}")
    print(f"  Labor Force:            {final['labor_force']:.2f}")
    print(f"  Final Stability:        {final['Stability']:.4f}")
    print(f"  Final Public Pool:      {final['Public_Pool']:.2f}")
    print(f"  Final Tax Rate:         {final['tax_rate']:.2%}")
    print(f"  Final Environment:      {final['Environment']:.4f}")
    print(f"  Final Resources:        {final['Resources']:.1f}")
    print(f"  Min Stability:          {df['Stability'].min():.4f}")
    print(f"  Max Stability:          {df['Stability'].max():.4f}")
    print(f"  Max Unemployment Rate:  {df['unemployment_rate'].max():.4f}")
    print(f"  Min Environment:        {df['Environment'].min():.4f}")

    collapse = df[df["Stability"] <= 0.01]
    if not collapse.empty:
        print(f"  Stability collapse at year: {collapse.iloc[0]['time']:.1f}")

    env_collapse = df[df["Environment"] <= 0.1]
    if not env_collapse.empty:
        print(f"  Environment collapse at year: {env_collapse.iloc[0]['time']:.1f}")

    depleted = df[df["Resources"] <= 0.01]
    if not depleted.empty:
        print(f"  Resource depletion at year: {depleted.iloc[0]['time']:.1f}")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.scenario == "custom":
        config = {
            "K_ai": args.k_ai,
            "Labor_U": args.labor_u,
            "Stability": args.stability,
            "Public_Pool": args.public_pool,
            "automation_speed": args.automation_speed,
            "churn_rate": args.churn_rate,
            "job_creation_rate": args.job_creation_rate,
            "retrain_rate": args.retrain_rate,
            "depreciation": args.depreciation,
            "stability_threshold": args.stability_threshold,
            "base_tax": args.base_tax,
            "max_tax": args.max_tax,
            "Environment": args.env_initial,
            "emission_rate": args.env_emission_rate,
            "emission_improvement_rate": args.env_emission_improvement,
            "absorption_capacity": args.env_absorption,
            "green_investment_factor": args.green_investment_factor,
            "env_output_sensitivity": args.env_output_sensitivity,
            "env_stability_sensitivity": args.env_stability_sensitivity,
            "Resources": args.resource_initial,
            "resource_use_rate": args.resource_use_rate,
            "resource_efficiency_rate": args.resource_efficiency_rate,
            "resource_scarcity_factor": args.resource_scarcity_factor,
        }
    else:
        config = SCENARIOS[args.scenario]()

    # ── Standard simulation ──
    model = AIWorldModel(**config)
    sim = Simulator(model)
    df = sim.run(t_end=args.t_end, dt=args.dt)

    print_summary(df)

    if args.output:
        df.to_csv(args.output, index=False)
        print(f"\nResults saved to {args.output}")

    stability_threshold = config.get("stability_threshold", 0.7)

    if args.plot or args.plot_file:
        fig = plot_simulation(df, title=f"AI-World3: {args.scenario}", stability_threshold=stability_threshold)
        if args.plot_file:
            save_plot(fig, args.plot_file)
            print(f"Plot saved to {args.plot_file}")
        if args.plot:
            show_plot(fig)

    # ── Sensitivity analysis ──
    if args.sensitivity_oat or args.sensitivity_lhs > 0:
        from ai_world3.sensitivity import (
            DEFAULT_LHS_RANGES,
            DEFAULT_OAT_RANGES,
            lhs_sample,
            multi_oat_sweep,
            rank_correlations,
        )
        from ai_world3.visualizer import plot_oat_sweep, plot_tornado

        # Build a base config dict (non-callable automation_speed only)
        base_config = {k: v for k, v in config.items() if not callable(v)}

        if args.sensitivity_oat:
            print("\n--- OAT Sensitivity Sweeps ---")
            oat_df = multi_oat_sweep(base_config, DEFAULT_OAT_RANGES, t_end=args.t_end, dt=max(args.dt, 0.5))
            if args.sensitivity_output:
                oat_df.to_csv(args.sensitivity_output.replace(".csv", "_oat.csv"), index=False)
            if args.sensitivity_plot:
                fig = plot_oat_sweep(oat_df, metric="final_stability")
                save_plot(fig, args.sensitivity_plot.replace(".png", "_oat.png"))
                print(f"OAT plot saved")

        if args.sensitivity_lhs > 0:
            print(f"\n--- LHS Sensitivity ({args.sensitivity_lhs} samples) ---")
            lhs_df = lhs_sample(base_config, DEFAULT_LHS_RANGES, n_samples=args.sensitivity_lhs, t_end=args.t_end, dt=max(args.dt, 0.5))
            param_names = list(DEFAULT_LHS_RANGES.keys())
            corr_df = rank_correlations(lhs_df, param_names, metric="final_stability")
            print(corr_df.to_string(index=False))
            if args.sensitivity_output:
                lhs_df.to_csv(args.sensitivity_output.replace(".csv", "_lhs.csv"), index=False)
                corr_df.to_csv(args.sensitivity_output.replace(".csv", "_corr.csv"), index=False)
            if args.sensitivity_plot:
                fig = plot_tornado(corr_df)
                save_plot(fig, args.sensitivity_plot.replace(".png", "_tornado.png"))
                print(f"Tornado plot saved")


if __name__ == "__main__":
    main()
