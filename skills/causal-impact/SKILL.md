---
name: causal-impact
description: "Estimate causal impact using difference-in-differences, synthetic control, propensity score matching, or instrumental variables."
aliases: [causal inference, did, synthetic control, propensity score, causal effect]
extends: spark
user_invocable: true
---

# Causal Impact

Estimate causal effects from observational data using established econometric methods. Supports difference-in-differences (with parallel trends testing), synthetic control (with placebo inference), propensity score matching (with balance diagnostics), and instrumental variables (with weak instrument tests). Includes robustness checks and sensitivity analysis.

## When to Use

- You cannot randomize and need to estimate a treatment effect from observational data
- You have a natural experiment or policy change and want to measure its causal impact
- You need to compare treated vs. control regions/cohorts with pre/post data (DiD)
- You want to build a synthetic counterfactual from donor units when no single control exists

## Workflow

1. **Env Check** -- Verify ab_utils.py and ml_utils.py are available; copy from extension templates if missing.
2. **Data Preparation** -- Load the dataset, identify treated/control groups and pre/post periods, validate that required columns are present, and check for sufficient pre-period observations.
3. **Causal Estimation** -- Apply the selected method (difference-in-differences, synthetic control, propensity score matching, or instrumental variables); compute the point estimate, standard error, confidence interval, and p-value; run method-specific diagnostics (parallel trends, covariate balance, instrument strength).

## Report Bus Integration

Produces `causal_impact_report.json` with the estimated effect, standard error, confidence interval, p-value, method-specific diagnostics (parallel trends test, balance table, or instrument F-statistic), and group means. Consumed by `ab-report` for the causal inference section.

## Full Specification

Usage: `/causal-impact <data_file> [--method did|synthetic_control|propensity|iv]`

Agent: **causal-analyst**

See `commands/causal-impact.md` for the complete workflow.
