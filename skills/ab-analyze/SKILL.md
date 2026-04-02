---
name: ab-analyze
description: "Analyze A/B test results with frequentist hypothesis testing, Bayesian posterior analysis, segmentation, and multiple comparison correction."
aliases: [ab test results, experiment analysis, ab testing, test results]
extends: ml-automation
user_invocable: true
---

# A/B Analyze

Comprehensive A/B test analysis combining frequentist and Bayesian methods. Validates data quality with SRM detection, computes p-values and confidence intervals, estimates posterior probabilities and expected loss, runs segmentation analysis for heterogeneous effects, and applies multiple comparison corrections.

## When to Use

- Your A/B test has finished collecting data and you need a full statistical readout
- You want both frequentist (p-values, CIs) and Bayesian (posterior, expected loss) perspectives in one pass
- You need to check for sample ratio mismatch before trusting experiment results
- You want to detect heterogeneous treatment effects across user segments

## Workflow

1. **Env Check** -- Verify ab_utils.py and ml_utils.py are available; copy from extension templates if missing.
2. **Data Validation** -- Load the experiment data file, confirm required columns exist, check for nulls, and run an SRM check on observed variant counts.
3. **Frequentist Analysis** -- Run a two-proportion z-test or Welch's t-test depending on metric type; compute p-value, confidence interval, effect size, and Cohen's d/h.
4. **Bayesian Analysis** -- Compute posterior distributions via Beta-Binomial (proportions) or Normal (continuous) model; report probability of treatment winning and expected loss.
5. **Segmentation** -- Slice results by user-specified segment columns, re-run frequentist and Bayesian tests per segment, and apply Benjamini-Hochberg FDR correction across segments.

## Report Bus Integration

Produces `ab_analyze_report.json` with frequentist results, Bayesian posteriors, per-segment breakdowns, and SRM diagnostics. Consumed by `ab-report` to generate the final experiment summary.

## Full Specification

Usage: `/ab-analyze <data_file> [--metric <col>] [--group <col>] [--segments <cols>] [--method both]`

Agent: **ab-analyst**

See `commands/ab-analyze.md` for the complete workflow.
