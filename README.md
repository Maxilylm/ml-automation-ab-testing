# spark-ab-testing

A/B testing and causal inference extension for [ml-automation](https://github.com/BLEND360/ml-automation-core).

## Prerequisites

- [ml-automation](https://github.com/BLEND360/ml-automation-core) core plugin (>= v1.8.0)
- Claude Code CLI
- Python 3.9+ with scipy/statsmodels for advanced statistical tests

## Installation

```bash
claude plugin add /path/to/spark-ab-testing
```

## What's Included

### Agents

| Agent | Purpose |
|---|---|
| `experiment-designer` | Power analysis, sample size, randomization, stratification |
| `ab-analyst` | Frequentist + Bayesian A/B testing, segmentation, multiple comparisons |
| `causal-analyst` | DiD, synthetic control, propensity score matching, instrumental variables |

### Commands

| Command | Purpose |
|---|---|
| `/ab-design` | Design experiment (power analysis, sample size, duration, randomization) |
| `/ab-analyze` | Analyze A/B test results (frequentist + Bayesian) |
| `/ab-bayesian` | Bayesian A/B testing with posterior distributions |
| `/ab-sequential` | Sequential testing with optional stopping rules |
| `/causal-impact` | Estimate causal impact (DiD, synthetic control, CausalImpact) |
| `/ab-report` | Generate experiment report with visualizations and recommendations |

## Getting Started

```bash
# Design an experiment
/ab-design proportion --mde 0.02 --power 0.8 --traffic 50000

# Analyze A/B test results
/ab-analyze experiment_data.csv --metric converted --group variant --method both

# Bayesian analysis with custom prior
/ab-bayesian experiment_data.csv --metric converted --prior beta:2,2 --rope 0.001

# Sequential testing
/ab-sequential experiment_data.csv --metric converted --method gst --spending obrien_fleming

# Causal impact estimation
/causal-impact sales_data.csv --method did --treatment-col treated --outcome-col revenue --time-col month

# Generate full report
/ab-report --format markdown --include-code
```

## How It Integrates

When installed alongside the core plugin:

1. **Automatic routing** -- Tasks mentioning A/B tests, experiment design, power analysis, or causal inference are routed to A/B testing agents
2. **Core workflow hooks** -- When running `/team-coldstart`:
   - `experiment-designer` fires at `after-eda` to detect experiment setups and suggest design improvements
   - `ab-analyst` fires at `after-evaluation` to add experiment-specific analysis
3. **Core agent reuse** -- Commands use eda-analyst, developer, ml-theory-advisor from core

## License

MIT
