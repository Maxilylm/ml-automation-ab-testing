# /causal-impact

Estimate causal impact of an intervention using observational data.

## Usage

```
/causal-impact <data_file> [--method <method>] [--treatment-col <column>] [--outcome-col <column>] [--time-col <column>] [--unit-col <column>]
```

- `data_file`: CSV/parquet with observational data
- `--method`: `did` (difference-in-differences), `synth` (synthetic control), `psm` (propensity score matching), `iv` (instrumental variables)
- `--treatment-col`: column indicating treatment status (0/1)
- `--outcome-col`: outcome variable column
- `--time-col`: time period column (required for DiD, synth)
- `--unit-col`: unit identifier column (required for panel methods)

## Workflow

### Stage 0: Environment Check

1. Check if `ml_utils.py` and `ab_utils.py` exist in `src/` — copy if missing
2. Verify data file and required columns exist

### Stage 1: Data Preparation

1. Load data, identify treatment/control units and time periods
2. For panel data: verify balanced panel (all units observed in all periods)
3. Identify pre-treatment and post-treatment periods
4. Report: unit counts, period counts, treatment timing, data summary

### Stage 2: Method-Specific Analysis

#### Difference-in-Differences (--method did)
1. Verify parallel trends assumption:
   - Visual inspection of pre-treatment trends
   - Formal test: interaction of group x time in pre-period
2. Estimate DiD coefficient: (Y_treat_post - Y_treat_pre) - (Y_ctrl_post - Y_ctrl_pre)
3. Cluster-robust standard errors (clustered at unit level)
4. Event study specification (dynamic treatment effects)

#### Synthetic Control (--method synth)
1. Select donor pool (untreated units)
2. Optimize weights to minimize pre-treatment RMSPE
3. Construct synthetic counterfactual
4. Estimate treatment effect: treated - synthetic
5. Placebo tests: apply method to each donor unit

#### Propensity Score Matching (--method psm)
1. Estimate propensity scores (logistic regression on covariates)
2. Assess common support (overlap of propensity distributions)
3. Match treated to control units (nearest neighbor, caliper=0.2*SD)
4. Verify covariate balance post-matching (SMD < 0.1)
5. Estimate ATT using `estimate_causal_impact()` from `ab_utils.py`

#### Instrumental Variables (--method iv)
1. Validate instrument relevance (first-stage F > 10)
2. Two-stage least squares estimation
3. Hausman test for endogeneity
4. Report LATE interpretation

### Stage 3: Robustness Checks

1. Sensitivity analysis (how much unmeasured confounding would invalidate results)
2. Placebo tests (fake treatment timing or fake treatment group)
3. Alternative specifications (different covariates, functional forms)
4. Report: robustness summary, sensitivity bounds

### Stage 4: Report

```python
from ml_utils import save_agent_report
save_agent_report("causal-analyst", {
    "status": "completed",
    "method": method,
    "causal_effect": {
        "estimate": point_estimate,
        "std_error": se,
        "ci_lower": ci_lo,
        "ci_upper": ci_hi,
        "p_value": p_value
    },
    "assumption_tests": assumption_results,
    "robustness_checks": robustness_results,
    "sample_sizes": {"treated": n_treated, "control": n_control},
    "recommendations": recommendations,
    "limitations": limitations
})
```

Write report to `reports/causal_impact_report.json`.
Print summary with effect estimate, assumption diagnostics, and caveats.
