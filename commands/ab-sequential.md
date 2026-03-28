# /ab-sequential

Sequential testing with optional stopping rules for A/B tests.

## Usage

```
/ab-sequential <data_file> [--metric <column>] [--group <column>] [--method <method>] [--alpha 0.05] [--spending <function>]
```

- `data_file`: CSV/parquet with per-user experiment data (ideally with timestamp)
- `--metric`: primary metric column
- `--group`: variant assignment column
- `--method`: `gst` (group sequential), `always_valid`, or `msprt` (default: gst)
- `--alpha`: overall significance level (default: 0.05)
- `--spending`: alpha spending function (`obrien_fleming`, `pocock`, `linear`) for GST

## Workflow

### Stage 0: Environment Check

1. Check if `ml_utils.py` and `ab_utils.py` exist in `src/` — copy if missing

### Stage 1: Test Configuration

1. Determine number of planned looks (interim analyses)
2. Configure alpha spending function:
   - O'Brien-Fleming: conservative early, aggressive late
   - Pocock: equal alpha at each look
   - Linear: proportional to information fraction
3. Compute adjusted critical values at each look
4. Report: number of looks, spending schedule, critical values

### Stage 2: Sequential Analysis

1. If data has timestamps, order chronologically and compute at each look:
   - Cumulative sample size per group
   - Cumulative test statistic (z-score or likelihood ratio)
   - Information fraction (current N / max N)
2. If no timestamps, treat current data as single look
3. Compare test statistic against boundary at current information fraction
4. Report: test statistic trajectory, boundary crossings

### Stage 3: Decision

1. Apply stopping rule:
   - **Reject H0**: test statistic crosses efficacy boundary — treatment works
   - **Accept H0**: test statistic crosses futility boundary — no effect
   - **Continue**: between boundaries — collect more data
2. Compute adjusted confidence interval (stage-wise ordering)
3. Compute conditional power (probability of eventual rejection given current data)
4. Report: decision, adjusted CI, conditional power

### Stage 4: Report

```python
from ml_utils import save_agent_report
save_agent_report("ab-analyst", {
    "status": "completed",
    "method": "sequential",
    "sequential_method": method,
    "spending_function": spending,
    "looks": [
        {"look": 1, "n": n1, "z_stat": z1, "boundary": b1, "decision": "continue"},
        {"look": 2, "n": n2, "z_stat": z2, "boundary": b2, "decision": "reject_h0"}
    ],
    "current_look": current_look,
    "information_fraction": info_frac,
    "decision": decision,
    "adjusted_ci": [ci_lo, ci_hi],
    "conditional_power": cond_power,
    "recommendations": recommendations
})
```

Write report to `reports/sequential_test_report.json`.
Print look-by-look summary with boundary visualization description.
