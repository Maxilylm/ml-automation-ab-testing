---
name: ab-bayesian
description: "Bayesian A/B testing with posterior distributions, ROPE analysis, expected loss, and decision rules for shipping or continuing experiments."
aliases: [bayesian ab, bayesian test, posterior analysis, bayesian experiment]
extends: ml-automation
user_invocable: true
---

# A/B Bayesian

Full Bayesian A/B testing workflow. Configures priors (uniform, weakly informative, or custom), computes posterior distributions analytically or via Monte Carlo sampling, calculates probability of treatment winning and expected loss, applies ROPE analysis for practical equivalence, and provides structured ship/kill/continue decisions.

## Full Specification

See `commands/ab-bayesian.md` for the complete workflow.
