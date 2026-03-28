# /ab-bayesian

Bayesian A/B testing with full posterior analysis and decision rules.

## Usage

```
/ab-bayesian <data_file> [--metric <column>] [--group <column>] [--prior <prior_spec>] [--rope <value>] [--samples 50000]
```

- `data_file`: CSV/parquet with per-user experiment data
- `--metric`: primary metric column
- `--group`: variant assignment column
- `--prior`: prior specification (`uniform`, `weakly_informative`, or `beta:a,b` / `normal:mu,sigma`)
- `--rope`: Region of Practical Equivalence threshold (default: 0.001 for proportions)
- `--samples`: Monte Carlo samples for posterior (default: 50000)

## Workflow

### Stage 0: Environment Check

1. Check if `ml_utils.py` and `ab_utils.py` exist in `src/` — copy if missing

### Stage 1: Prior Specification

1. Set prior based on `--prior` flag:
   - `uniform`: Beta(1,1) for proportions, broad Normal for continuous
   - `weakly_informative`: Beta(2,2) or Normal centered on historical mean
   - Custom: parse `beta:a,b` or `normal:mu,sigma`
2. Report: prior parameters and interpretation

### Stage 2: Posterior Computation

1. Load data, compute sufficient statistics per group
2. Update prior to posterior analytically (conjugate) or via sampling
3. Draw `--samples` from each group's posterior distribution
4. Report: posterior summary (mean, median, mode, HDI)

### Stage 3: Comparison

1. Compute P(treatment > control) from paired samples
2. Compute distribution of (treatment - control) — the lift distribution
3. Expected loss: E[max(control - treatment, 0)]
4. ROPE analysis: P(|effect| < rope) — probability of practical equivalence
5. Report: probability of winning, expected loss, ROPE probability

### Stage 4: Decision Rules

1. Apply decision framework:
   - **Ship**: P(treatment > control) > 0.95 AND expected loss < threshold
   - **Kill**: P(control > treatment) > 0.95
   - **Continue**: neither condition met (need more data)
2. Compute expected remaining samples to reach decision (if continue)
3. Report: decision, supporting evidence, risk quantification

### Stage 5: Report

```python
from ml_utils import save_agent_report
save_agent_report("ab-analyst", {
    "status": "completed",
    "method": "bayesian",
    "prior": prior_spec,
    "posterior": {
        "control": {"mean": c_mean, "hdi_95": [c_lo, c_hi]},
        "treatment": {"mean": t_mean, "hdi_95": [t_lo, t_hi]}
    },
    "prob_treatment_better": prob_better,
    "expected_loss": expected_loss,
    "rope_probability": rope_prob,
    "lift_distribution": {"mean": lift_mean, "hdi_95": [lift_lo, lift_hi]},
    "decision": decision,
    "recommendations": recommendations
})
```

Write report to `reports/bayesian_ab_report.json`.
Print posterior summary with visualization description.
