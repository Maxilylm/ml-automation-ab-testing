# /ab-design

Design an A/B test experiment with power analysis, sample size calculation, and randomization strategy.

## Usage

```
/ab-design <metric_type> [--mde <effect_size>] [--alpha 0.05] [--power 0.8] [--variants 2] [--traffic <daily_users>]
```

- `metric_type`: `proportion` (conversion rate) or `continuous` (revenue, time)
- `--mde`: minimum detectable effect (absolute or relative, default: 0.02 for proportion, 5% relative for continuous)
- `--alpha`: significance level (default: 0.05)
- `--power`: statistical power (default: 0.8)
- `--variants`: number of variants including control (default: 2)
- `--traffic`: daily traffic volume for duration estimation

## Workflow

### Stage 0: Environment Check

1. Check if `ml_utils.py` exists in `src/` — if missing, copy from core plugin (`~/.claude/plugins/*/templates/ml_utils.py`)
2. Check if `ab_utils.py` exists in `src/` — if missing, copy from this plugin's `templates/ab_utils.py`

### Stage 1: Metric Definition

1. Identify metric type (proportion or continuous)
2. Gather baseline metric values:
   - For proportions: current conversion rate (e.g., 0.12)
   - For continuous: current mean and standard deviation
3. Define primary metric (OEC) and guardrail metrics
4. Report: metric type, baseline values, target effect size

### Stage 2: Power Analysis

1. Compute minimum sample size per variant using `compute_sample_size()`:
   - Proportions: normal approximation for two-proportion z-test
   - Continuous: two-sample t-test formula
   - Multi-arm: apply Bonferroni correction to alpha
2. Generate power curve (sample size vs. MDE at fixed power)
3. Report: required N per variant, total N, power curve summary

### Stage 3: Duration Estimation

1. Given `--traffic` (daily users), compute:
   - Minimum days = total_N / (daily_traffic * traffic_allocation)
   - Add burn-in period (3-7 days for novelty effects)
   - Round up to full weeks (capture day-of-week effects)
2. Flag if duration exceeds 8 weeks (cost/opportunity risk)
3. Report: estimated days, recommended start/end, warnings

### Stage 4: Randomization Strategy

1. Recommend randomization unit (user-level by default)
2. Suggest stratification variables (platform, region, user tier)
3. Compute expected covariate balance at target sample size
4. Output: randomization config with hash-based assignment pseudocode

### Stage 5: Design Report

```python
from ml_utils import save_agent_report
save_agent_report("experiment-designer", {
    "status": "completed",
    "metric_type": metric_type,
    "baseline": baseline_value,
    "mde": mde,
    "alpha": alpha,
    "power": power,
    "sample_size_per_variant": n_per_variant,
    "total_sample_size": total_n,
    "variants": num_variants,
    "estimated_days": estimated_days,
    "randomization_unit": "user",
    "stratification": stratification_vars,
    "recommendations": recommendations
})
```

Write design document to `reports/experiment_design.json`.
Print summary table with all design parameters.
