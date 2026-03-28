# /ab-report

Generate a comprehensive experiment report with visualizations and recommendations.

## Usage

```
/ab-report [--experiment-dir <path>] [--format <format>] [--include-code]
```

- `--experiment-dir`: directory containing experiment data and prior analysis reports (default: current directory)
- `--format`: output format `html`, `markdown`, or `json` (default: markdown)
- `--include-code`: include reproducible Python code snippets in the report

## Workflow

### Stage 0: Environment Check

1. Check if `ml_utils.py` and `ab_utils.py` exist in `src/` — copy if missing
2. Scan for existing agent reports (`*_report.json`) from prior analysis commands

### Stage 1: Gather Results

1. Load all available reports:
   - `experiment-designer` report (design parameters)
   - `ab-analyst` report (frequentist + Bayesian results)
   - `causal-analyst` report (causal inference results)
2. Load raw experiment data if available
3. Report: which reports found, data availability

### Stage 2: Executive Summary

1. One-paragraph summary of the experiment:
   - What was tested (hypothesis)
   - What was found (effect size and significance)
   - What to do (ship, iterate, kill)
2. Key metrics table: metric, control, treatment, difference, p-value, CI

### Stage 3: Detailed Results

1. **Design Section**: sample size, power, duration, randomization
2. **Data Quality**: SRM check, covariate balance, missing data
3. **Frequentist Results**: p-values, confidence intervals, effect sizes
4. **Bayesian Results**: posterior probabilities, expected loss, credible intervals
5. **Segmentation**: treatment effects by segment (if available)
6. **Causal Analysis**: DiD/synth/PSM results (if available)

### Stage 4: Visualizations

1. Generate visualization descriptions and Python code:
   - Conversion funnel comparison (control vs. treatment)
   - Metric distribution by group (histogram/KDE)
   - Bayesian posterior distributions
   - Cumulative effect over time (sequential monitoring)
   - Segment-level treatment effects (forest plot)
   - Power curve from design phase
2. If `--include-code`: include matplotlib/seaborn code blocks

### Stage 5: Recommendations

1. Statistical recommendation (based on significance and effect size)
2. Business recommendation (effect magnitude vs. implementation cost)
3. Follow-up experiments (if inconclusive or new hypotheses emerged)
4. Guardrail assessment (any guardrail metrics degraded?)

### Stage 6: Write Report

```python
from ml_utils import save_agent_report
save_agent_report("ab-analyst", {
    "status": "completed",
    "report_type": "experiment_summary",
    "format": output_format,
    "sections": ["executive_summary", "design", "data_quality",
                 "frequentist", "bayesian", "segments", "recommendations"],
    "recommendation": final_recommendation,
    "report_path": report_path
})
```

Write report to `reports/experiment_report.{md|html|json}`.
Print executive summary to console.
