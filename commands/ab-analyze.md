# /ab-analyze

Analyze A/B test results with both frequentist and Bayesian methods.

## Usage

```
/ab-analyze <data_file> [--metric <column>] [--group <column>] [--segments <columns>] [--method both]
```

- `data_file`: CSV/parquet with per-user experiment data
- `--metric`: column name for the primary metric (default: auto-detect)
- `--group`: column name for variant assignment (default: `variant` or `group`)
- `--segments`: comma-separated columns for segmentation analysis
- `--method`: `frequentist`, `bayesian`, or `both` (default: both)

## Workflow

### Stage 0: Environment Check

1. Check if `ml_utils.py` exists in `src/` — if missing, copy from core plugin
2. Check if `ab_utils.py` exists in `src/` — if missing, copy from this plugin's `templates/ab_utils.py`
3. Verify data file exists and is readable

### Stage 1: Data Validation

1. Load experiment data, identify group and metric columns
2. Check for sample ratio mismatch (SRM):
   - Chi-squared test on observed vs. expected group sizes
   - Flag if p < 0.001 (strong evidence of assignment bias)
3. Compute per-group summary stats (N, mean, std, conversion rate)
4. Report: group sizes, SRM test result, metric summaries

### Stage 2: Frequentist Analysis

1. Run `run_frequentist_test()` from `ab_utils.py`:
   - Proportions: two-proportion z-test
   - Continuous: Welch's t-test
2. Compute:
   - p-value (two-sided)
   - Confidence interval for treatment effect (absolute and relative)
   - Cohen's d / h effect size
3. Report: p-value, CI, effect size, significant at alpha=0.05?

### Stage 3: Bayesian Analysis

1. Run `run_bayesian_test()` from `ab_utils.py`:
   - Proportions: Beta(1,1) prior, posterior Beta(a+successes, b+failures)
   - Continuous: Normal-Inverse-Gamma conjugate prior
2. Compute:
   - P(treatment > control) via Monte Carlo sampling
   - Expected loss of choosing treatment
   - 95% credible interval for effect size
3. Report: posterior probability, expected loss, credible interval

### Stage 4: Segmentation Analysis (if --segments provided)

1. For each segment variable:
   - Split data by segment values
   - Run frequentist test within each segment
   - Compute interaction effect (segment x treatment)
2. Flag segments with significantly different treatment effects
3. Report: per-segment treatment effects, interaction p-values

### Stage 5: Multiple Comparison Adjustment

1. If multiple metrics analyzed:
   - Apply Benjamini-Hochberg FDR correction
   - Report adjusted p-values alongside raw p-values
2. Report: adjusted significance decisions

### Stage 6: Results Report

```python
from ml_utils import save_agent_report
save_agent_report("ab-analyst", {
    "status": "completed",
    "sample_sizes": {"control": n_control, "treatment": n_treatment},
    "srm_test": {"chi2": chi2, "p_value": srm_p, "alert": srm_alert},
    "frequentist": {
        "p_value": p_value,
        "ci_lower": ci_lo,
        "ci_upper": ci_hi,
        "effect_size": effect_size,
        "significant": is_significant
    },
    "bayesian": {
        "prob_treatment_better": prob_better,
        "expected_loss": expected_loss,
        "credible_interval": [ci_lo, ci_hi]
    },
    "segments": segment_results,
    "recommendation": recommendation
})
```

Write report to `reports/ab_analysis_report.json`.
Print summary with decision recommendation (ship / iterate / kill).
