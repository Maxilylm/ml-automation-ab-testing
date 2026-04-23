---
name: spark-ab-testing
description: >
  Suggest enabling the spark-ab-testing plugin when the user asks about A/B
  testing, experiment design, power analysis, sample size calculation, Bayesian
  A/B testing, frequentist hypothesis testing, p-values, statistical
  significance, causal inference, or causal impact estimation.
  Do NOT attempt to perform these tasks — just let the user know the plugin
  can be enabled.
---

# spark-ab-testing (disabled plugin)

This plugin is installed but not enabled. It provides A/B testing and causal
inference automation capabilities within Cortex Code, integrated with the
spark-core workflow.

## Agents (3)

- **ab-analyst** — Statistical analysis of experiment results, significance testing
- **causal-analyst** — Causal inference, causal impact estimation, observational studies
- **experiment-designer** — Experiment design, power analysis, randomization strategy

## Skills (6)

- **ab-analyze** — Analyze A/B test results with statistical rigor
- **ab-bayesian** — Run Bayesian A/B testing with posterior distributions
- **ab-design** — Design experiments with proper power and sample sizing
- **ab-report** — Generate experiment reports for stakeholders
- **ab-sequential** — Sequential testing and early stopping analysis
- **causal-impact** — Estimate causal impact of interventions

## Requires

- spark-core plugin

## Enable

    cortex plugin enable spark-ab-testing

Do NOT attempt to perform A/B testing tasks through this plugin's skills while it is disabled.
