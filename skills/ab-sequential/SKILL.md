---
name: ab-sequential
description: "Sequential testing with alpha spending functions and optional stopping rules for A/B experiments."
aliases: [sequential test, optional stopping, group sequential, early stopping]
extends: spark
user_invocable: true
---

# A/B Sequential

Sequential testing for A/B experiments with valid early stopping. Supports group sequential tests with alpha spending functions (O'Brien-Fleming, Pocock), always-valid inference, and mixture sequential probability ratio tests. Tracks test statistic trajectories against boundaries and provides adjusted confidence intervals.

## When to Use

- You want to monitor an A/B test continuously and stop early if a clear winner emerges
- You need valid p-values and confidence intervals despite multiple interim looks at the data
- Your experiment has high opportunity cost and you cannot afford to wait for the full sample
- You want to control Type I error while allowing flexible stopping with alpha spending

## Workflow

1. **Env Check** -- Verify ab_utils.py and ml_utils.py are available; copy from extension templates if missing.
2. **Test Configuration** -- Define the number of planned interim analyses (looks), select an alpha spending function (O'Brien-Fleming, Pocock, or custom), and set the overall significance level.
3. **Sequential Monitoring** -- At each interim look, compute the test statistic, compare against the spending-adjusted boundary, report whether to stop for efficacy, stop for futility, or continue; produce adjusted confidence intervals that remain valid at any stopping point.

## Report Bus Integration

Produces `ab_sequential_report.json` with boundary values per look, observed test statistics, spending function used, stop/continue decision at each interim analysis, and adjusted confidence intervals. Consumed by `ab-report` for the sequential monitoring section.

## Full Specification

Usage: `/ab-sequential <data_file> [--metric <col>] [--group <col>] [--spending <function>]`

Agent: **ab-analyst**

See `commands/ab-sequential.md` for the complete workflow.
