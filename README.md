# AI-World3

**A system dynamics model exploring the long-term interplay between AI automation, employment, social stability, and environmental limits.**

Inspired by the [World3 model](https://en.wikipedia.org/wiki/World3) from the 1972 *Limits to Growth* study, AI-World3 uses stock-and-flow dynamics with feedback loops to examine how different policy and technology choices shape outcomes over 100–200 year horizons. It tracks six interacting state variables — AI capital, unemployment, social stability, public fiscal capacity, environmental quality, and natural resources — connected through reinforcing and balancing feedback loops.

Five scenarios explore the space from no intervention to aggressive welfare states to exponential automation and green technology paths. The central finding: social policy alone is insufficient. Even the strongest safety net fails to prevent environmental collapse. Only combined social and technology policy sustains both dimensions — and even that requires politically painful persistence through an early crisis that the policy itself helps create.

![Cross-scenario comparison](paper_comparison.png)

> This model, its analysis, and its [accompanying paper](AI-World3-Analysis.md) were developed through human-AI collaboration: the author provided direction and judgment while Claude (Anthropic) designed, implemented, debugged, and analyzed the model. See the paper's introduction for details.

## Key findings

- **Social policy alone doesn't save the environment.** The Nordic scenario achieves 4% unemployment but the environment collapses anyway — the employment and environmental feedback loops are structurally decoupled.
- **Every intervention scenario passes through a stability crisis** driven largely by the fiscal burden of the intervention itself. The political cost of doing the right thing is modeled, not assumed away.
- **Automation speed matters less than institutional capacity.** Sensitivity analysis shows resource and emission dynamics dominate outcomes; the pace of AI matters less than whether institutions can retrain, create sectors, and invest in clean technology.
- **Exponential automation overwhelms linear policy tools.** The Singularity scenario fails not through mass unemployment but through cascading environmental collapse during rapid growth.
- **The model assumes policy persistence** — no political reversal, no populist backlash. Real democracies may oscillate between intervention and abandonment, potentially producing worse outcomes than either consistent path.

## Scenarios

| Scenario         | Unemployment | Environment | Stability                   | Outcome         |
| ---------------- | ------------ | ----------- | --------------------------- | --------------- |
| Laissez-Faire    | 48.8%        | Collapse    | Collapse → partial recovery | Collapse        |
| Nordic AI        | 4.0%         | Collapse    | Crash → full recovery       | Partial success |
| Singularity      | 10.2%        | Collapse    | Crash → recovery            | Collapse        |
| Green Transition | 7.7%         | Sustained   | Dip → recovery              | Sustained       |
| Extraction       | 131.6%       | Collapse    | Permanent collapse          | Total collapse  |

## Installation

Requires Python 3.10+.

```bash
pip install -e .
```

Or with dev dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

Run a predefined scenario:

```bash
ai-world3 nordic --t-end 200 --plot
```

Save results to CSV and plot to file:

```bash
ai-world3 green-transition --t-end 200 --output results.csv --plot-file green.png
```

Run all scenarios:

```bash
for s in laissez-faire nordic singularity green-transition extraction; do
  ai-world3 $s --t-end 200 --plot-file "${s}.png"
done
```

Run sensitivity analysis (Latin Hypercube Sampling):

```bash
ai-world3 nordic --sensitivity-lhs 100 --sensitivity-plot tornado.png
```

Run one-at-a-time parameter sweeps:

```bash
ai-world3 nordic --sensitivity-oat --sensitivity-plot oat_sweeps.png
```

Custom scenario with specific parameters:

```bash
ai-world3 custom --automation-speed 0.08 --stability-threshold 0.75 \
  --env-emission-rate 0.001 --t-end 150 --plot
```

## Project structure

```
ai-world3/
├── src/ai_world3/
│   ├── model.py          # Core AIWorldModel — six ODEs, ~20 parameters
│   ├── simulator.py      # Forward Euler integrator, DataFrame output
│   ├── scenarios.py      # Five predefined scenario configurations
│   ├── sensitivity.py    # OAT sweeps and Latin Hypercube Sampling
│   ├── visualizer.py     # 3x3 dashboards, tornado plots, comparisons
│   └── cli.py            # Command-line interface
├── tests/
│   ├── test_model.py     # 53 tests covering all model mechanisms
│   ├── test_scenarios.py # Scenario-level behavioral assertions
│   └── test_simulator.py # Integration and output format tests
├── AI-World3-Analysis.md # Full analysis paper
├── paper_*.png           # Publication-quality scenario plots
└── pyproject.toml
```

## The model

Six state variables integrated with forward Euler (dt=0.1 years):

- **K_ai** — AI capital stock (grows via investment, decays via depreciation)
- **Labor_U** — Unemployed workers (displaced by automation, restored by job creation and retraining)
- **Stability** — Social stability index 0–1 (drained by unemployment, taxes, and environmental stress)
- **Public_Pool** — Fiscal capacity for retraining and UBI (funded by taxation)
- **Environment** — Environmental quality 0–1 (degraded by emissions, restored by absorption with tipping-point dynamics)
- **Resources** — Finite resource stock (monotonic depletion with efficiency improvements)

Key mechanisms include hybrid displacement (growth-driven + churn), Michaelis-Menten job creation saturation, structural mismatch friction, institutional retraining throughput limits, dynamic emission intensity improvement, and stability-linked environmental absorption. See the [full paper](AI-World3-Analysis.md) for details.

## Tests

```bash
pytest
```

All 53 tests cover initial conditions, hybrid displacement, job creation saturation, mismatch friction, retraining throughput, dynamic emission/resource mechanisms, symmetric stability normalization, and scenario-level behavioral properties.

## Documentation

- [**AI-World3-Analysis.md**](AI-World3-Analysis.md) — Full analysis paper with historical context, model description, scenario results, sensitivity analysis, and discussion of limitations
- 

## License

MIT

## Author

Janne Haarni — February 2026

*Built with Claude (Anthropic)*
