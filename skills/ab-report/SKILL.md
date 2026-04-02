---
name: ab-report
description: "Generate comprehensive experiment reports with executive summary, visualizations, and ship/kill/iterate recommendations."
aliases: [experiment report, ab report, test report, experiment summary]
extends: spark
user_invocable: true
---

# A/B Report

Generate a complete experiment report by aggregating results from design, analysis, and causal inference stages. Produces an executive summary, detailed results sections (frequentist, Bayesian, segmentation, causal), visualization code, and actionable recommendations with business context.

## When to Use

- Your experiment analysis is complete and you need a stakeholder-ready report
- You want to consolidate frequentist, Bayesian, sequential, and causal results into one document
- You need a structured ship/kill/iterate recommendation backed by statistical evidence
- You want auto-generated visualization code (matplotlib/plotly) alongside the narrative

## Workflow

1. **Env Check** -- Verify ab_utils.py and ml_utils.py are available; copy from extension templates if missing.
2. **Gather Results** -- Load all available report bus files (ab_design_report, ab_analyze_report, ab_bayesian_report, ab_sequential_report, causal_impact_report) from the experiment directory.
3. **Generate Report** -- Assemble the final document in the requested format (HTML, PDF, or Markdown) with: executive summary, experiment design recap, frequentist and Bayesian results, segmentation findings, causal impact estimates, visualization code blocks, and a closing recommendation section with confidence level and caveats.

## Report Bus Integration

Reads all upstream `*_report.json` files produced by other ab-testing commands. Produces `ab_experiment_report.json` as a manifest linking to the generated report file and summarizing the overall recommendation.

## Full Specification

Usage: `/ab-report [--experiment-dir <path>] [--format html|pdf|md]`

Agent: **ab-analyst**

See `commands/ab-report.md` for the complete workflow.
