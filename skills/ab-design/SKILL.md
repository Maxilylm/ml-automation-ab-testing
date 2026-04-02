---
name: ab-design
description: "Design A/B test experiments with power analysis, sample size calculation, duration estimation, and randomization strategy."
aliases: [experiment design, power analysis, sample size, test design]
extends: spark
user_invocable: true
---

# A/B Design

Design A/B test experiments end-to-end. Computes minimum sample size via power analysis for proportion or continuous metrics, estimates experiment duration given traffic volume, recommends randomization strategy and stratification variables, and outputs a complete experiment design document.

## When to Use

- You need to determine sample size before launching an A/B test
- You want a power analysis for a new experiment with a specific MDE target
- You need to estimate how long an experiment should run given daily traffic
- You are planning a multi-variant test and need Bonferroni-adjusted sizing

## Workflow

1. **Env Check** -- Verify ab_utils.py and ml_utils.py are available in project; copy from extension templates if missing.
2. **Metric Definition** -- Identify whether the primary metric is a proportion (e.g., conversion rate) or continuous (e.g., revenue per user), and establish the baseline value.
3. **Power Analysis** -- Compute the minimum detectable effect, significance level, and statistical power; generate a power curve across a range of MDE values.
4. **Sample Size Calculation** -- Derive per-variant sample size using the two-proportion z-test or two-sample t-test formula, adjusting for multiple comparisons when variants > 2.
5. **Duration Estimation** -- Combine sample size with daily eligible traffic to estimate calendar days required, accounting for weekday/weekend traffic variation.

## Report Bus Integration

Produces `ab_design_report.json` containing `n_per_variant`, `total_n`, power curve data, duration estimate, and full parameter set. Downstream commands (`ab-analyze`, `ab-report`) read this report to validate that collected data meets the original design.

## Full Specification

Usage: `/ab-design <metric_type> [--mde <effect>] [--alpha 0.05] [--power 0.8] [--traffic <daily_users>]`

Agent: **experiment-designer**

See `commands/ab-design.md` for the complete workflow.
