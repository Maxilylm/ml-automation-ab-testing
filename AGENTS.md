# spark-ab-testing — Cortex Code Extension

A/B testing and causal inference. Experiment design, power analysis, Bayesian and frequentist testing, sequential testing, and causal impact estimation. Requires spark-core installed.

## Available Agents

| Agent | When to use |
|---|---|
| `experiment-designer` | User wants to design an A/B experiment, calculate sample size, determine test duration, or choose a testing methodology |
| `ab-analyst` | User wants to analyze experiment results using frequentist or Bayesian statistics |
| `causal-analyst` | User wants causal inference, difference-in-differences, synthetic control, or CausalImpact analysis |

## Available Skills

| Skill | Trigger |
|---|---|
| `/ab-design` | "design an A/B test", "calculate sample size", "plan an experiment", "power analysis" |
| `/ab-analyze` | "analyze A/B results", "is this significant", "compare control and treatment" |
| `/ab-bayesian` | "Bayesian A/B test", "probability of being best", "Bayesian analysis of experiment" |
| `/ab-sequential` | "sequential testing", "always-valid inference", "early stopping rules" |
| `/causal-impact` | "causal impact analysis", "diff-in-diff", "synthetic control", "did this intervention work" |
| `/ab-report` | "A/B test report", "experiment summary", "results presentation" |

## Routing

- Experiment design, power analysis → `experiment-designer`
- Statistical analysis of results → `ab-analyst`
- Causal inference, observational studies → `causal-analyst`
- Fallback → spark-core orchestrator
