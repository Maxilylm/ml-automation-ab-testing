---
name: ab-bayesian
description: "Bayesian A/B testing with posterior distributions, ROPE analysis, expected loss, and decision rules for shipping or continuing experiments."
aliases: [bayesian ab, bayesian test, posterior analysis, bayesian experiment]
extends: ml-automation
user_invocable: true
---

# A/B Bayesian

Full Bayesian A/B testing workflow. Configures priors (uniform, weakly informative, or custom), computes posterior distributions analytically or via Monte Carlo sampling, calculates probability of treatment winning and expected loss, applies ROPE analysis for practical equivalence, and provides structured ship/kill/continue decisions.

## When to Use

- You prefer Bayesian inference over null-hypothesis testing for experiment decisions
- You need to incorporate prior knowledge or historical data into the analysis
- You want a direct probability statement ("95% chance treatment is better") rather than a p-value
- You need ROPE (Region of Practical Equivalence) analysis to distinguish meaningful effects from noise

## Workflow

1. **Env Check** -- Verify ab_utils.py and ml_utils.py are available; copy from extension templates if missing.
2. **Prior Specification** -- Select or define the prior distribution: Beta(1,1) uniform, weakly informative based on historical rates, or a fully custom prior supplied via `--prior`.
3. **Posterior Sampling** -- Update the prior with observed data to obtain posterior distributions; use analytic conjugate updates for proportions, Monte Carlo sampling (50k draws) for continuous metrics.
4. **Decision Rules** -- Compute probability of treatment being best, expected loss if shipping treatment, ROPE overlap, and credible intervals; emit a ship/kill/continue recommendation with confidence level.

## Report Bus Integration

Produces `ab_bayesian_report.json` with posterior parameters, probability of winning, expected loss, ROPE analysis, credible intervals, and the final decision recommendation. Consumed by `ab-report` for the Bayesian section of the experiment summary.

## Full Specification

Usage: `/ab-bayesian <data_file> [--metric <col>] [--group <col>] [--prior <spec>] [--rope <value>]`

Agent: **ab-analyst**

See `commands/ab-bayesian.md` for the complete workflow.
