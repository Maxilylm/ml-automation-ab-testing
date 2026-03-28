"""
A/B testing and causal inference utilities for the ml-automation-ab-testing extension plugin.

Requires ml_utils.py from the ml-automation core plugin to be present
in the same directory (copied via Stage 0 of A/B testing commands).
"""

import os
import json
import math
import random
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

from ml_utils import save_agent_report, load_agent_report


# --- Relevance Detection ---

EXPERIMENT_INDICATORS = {
    "scipy.stats",
    "statsmodels",
    "pymc",
    "arviz",
    "causalimpact",
    "dowhy",
    "econml",
    "optimizely",
    "launchdarkly",
    "eppo",
    "statsig",
    "growthbook",
}

EXPERIMENT_COLUMN_PATTERNS = [
    "variant",
    "treatment",
    "control",
    "group",
    "experiment_id",
    "bucket",
    "arm",
    "ab_group",
]


def detect_experiment_relevance(project_path="."):
    """Check if project has A/B testing or experiment indicators for relevance gating.

    Checks: experiment library imports, treatment/control columns in data files,
    experiment configuration files, feature flag SDKs.

    Args:
        project_path: root directory of the project

    Returns:
        dict with 'is_experiment': bool, 'indicators': list of found indicators
    """
    indicators = []
    project = Path(project_path)

    # Check requirements for experiment packages
    for req_file in ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"]:
        req_path = project / req_file
        if req_path.exists():
            content = req_path.read_text().lower()
            for pkg in EXPERIMENT_INDICATORS:
                if pkg.replace(".", "-") in content or pkg in content:
                    indicators.append(f"{pkg} in {req_file}")

    # Check Python files for experiment-related imports
    py_files = list(project.glob("**/*.py"))[:50]  # limit scan
    for py_file in py_files:
        try:
            content = py_file.read_text()
            for pkg in EXPERIMENT_INDICATORS:
                if f"import {pkg}" in content or f"from {pkg}" in content:
                    indicators.append(f"{pkg} import in {py_file.name}")
                    break
            # Check for scipy.stats specific imports
            if "from scipy import stats" in content or "from scipy.stats import" in content:
                indicators.append(f"scipy.stats import in {py_file.name}")
        except (UnicodeDecodeError, PermissionError):
            continue

    # Check CSV headers for experiment columns
    csv_files = list(project.glob("**/*.csv"))[:10]
    for csv_file in csv_files:
        try:
            with open(csv_file) as f:
                header = f.readline().strip().lower()
                for col_pattern in EXPERIMENT_COLUMN_PATTERNS:
                    if col_pattern in header:
                        indicators.append(f"Column '{col_pattern}' in {csv_file.name}")
                        break
        except (UnicodeDecodeError, PermissionError):
            continue

    # Check for experiment config files
    config_patterns = ["experiment*.json", "experiment*.yaml", "experiment*.yml",
                       "ab_test*.json", "ab_test*.yaml"]
    for pattern in config_patterns:
        config_files = list(project.glob(f"**/{pattern}"))
        if config_files:
            indicators.append(f"Experiment config: {config_files[0].name}")

    # Check for feature flag configs
    for ff_file in [".optimizely.json", ".launchdarkly.json", ".eppo.json",
                    ".statsig.json", ".growthbook.json"]:
        if (project / ff_file).exists():
            indicators.append(f"Feature flag config: {ff_file}")

    return {
        "is_experiment": len(indicators) > 0,
        "indicators": indicators,
    }


# --- Sample Size & Power Analysis ---

def _normal_cdf(x):
    """Standard normal CDF using error function approximation."""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _normal_ppf(p):
    """Standard normal inverse CDF (percent point function).

    Uses rational approximation (Abramowitz and Stegun 26.2.23).
    """
    if p <= 0 or p >= 1:
        raise ValueError("p must be between 0 and 1 exclusive")

    if p < 0.5:
        return -_normal_ppf(1 - p)

    t = math.sqrt(-2 * math.log(1 - p))
    # Rational approximation constants
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    return t - (c0 + c1 * t + c2 * t * t) / (1 + d1 * t + d2 * t * t + d3 * t * t * t)


def compute_sample_size(baseline, mde, alpha=0.05, power=0.8,
                        metric_type="proportion", variants=2):
    """Compute minimum sample size per variant for an A/B test.

    Args:
        baseline: baseline metric value (e.g., 0.12 for 12% conversion rate)
        mde: minimum detectable effect (absolute change, e.g., 0.02)
        alpha: significance level (default: 0.05)
        power: statistical power (default: 0.8)
        metric_type: 'proportion' or 'continuous'
        variants: number of variants including control (default: 2)

    Returns:
        dict with 'n_per_variant', 'total_n', 'parameters'
    """
    # Adjust alpha for multiple comparisons (Bonferroni)
    adjusted_alpha = alpha / max(variants - 1, 1)

    z_alpha = _normal_ppf(1 - adjusted_alpha / 2)
    z_beta = _normal_ppf(power)

    if metric_type == "proportion":
        p1 = baseline
        p2 = baseline + mde
        # Two-proportion z-test sample size formula
        pooled_p = (p1 + p2) / 2
        n = ((z_alpha * math.sqrt(2 * pooled_p * (1 - pooled_p)) +
              z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) / mde) ** 2
    elif metric_type == "continuous":
        # Two-sample t-test formula (assumes equal variance)
        # baseline here is the standard deviation
        sigma = baseline
        n = 2 * ((z_alpha + z_beta) * sigma / mde) ** 2
    else:
        raise ValueError(f"Unknown metric_type: {metric_type}")

    n_per_variant = math.ceil(n)

    return {
        "n_per_variant": n_per_variant,
        "total_n": n_per_variant * variants,
        "parameters": {
            "baseline": baseline,
            "mde": mde,
            "alpha": alpha,
            "adjusted_alpha": round(adjusted_alpha, 6),
            "power": power,
            "metric_type": metric_type,
            "variants": variants,
        },
    }


def power_curve(baseline, alpha=0.05, power=0.8, metric_type="proportion",
                mde_range=None):
    """Generate power curve data: sample size vs. MDE.

    Args:
        baseline: baseline metric value
        alpha: significance level
        power: statistical power
        metric_type: 'proportion' or 'continuous'
        mde_range: list of MDE values to evaluate (default: auto-generated)

    Returns:
        list of dicts with 'mde' and 'n_per_variant'
    """
    if mde_range is None:
        if metric_type == "proportion":
            # Range from 0.5% to 10% absolute
            mde_range = [round(x * 0.005, 4) for x in range(1, 21)]
        else:
            # Range from 1% to 20% of baseline
            mde_range = [round(baseline * x * 0.01, 4) for x in range(1, 21)]

    curve = []
    for mde in mde_range:
        if mde <= 0:
            continue
        result = compute_sample_size(baseline, mde, alpha, power, metric_type)
        curve.append({
            "mde": mde,
            "n_per_variant": result["n_per_variant"],
            "total_n": result["total_n"],
        })

    return curve


# --- Frequentist Testing ---

def run_frequentist_test(control_data, treatment_data, metric_type="proportion",
                         alpha=0.05):
    """Run frequentist hypothesis test for A/B experiment.

    Args:
        control_data: list of values for control group
            - For proportions: list of 0/1 (conversion indicators)
            - For continuous: list of metric values
        treatment_data: list of values for treatment group
        metric_type: 'proportion' or 'continuous'
        alpha: significance level

    Returns:
        dict with 'p_value', 'ci_lower', 'ci_upper', 'effect_size',
        'relative_effect', 'significant', 'test_statistic'
    """
    n_c = len(control_data)
    n_t = len(treatment_data)

    if metric_type == "proportion":
        # Two-proportion z-test
        p_c = sum(control_data) / n_c
        p_t = sum(treatment_data) / n_t
        effect = p_t - p_c

        pooled_p = (sum(control_data) + sum(treatment_data)) / (n_c + n_t)
        se_pooled = math.sqrt(pooled_p * (1 - pooled_p) * (1 / n_c + 1 / n_t))
        se_effect = math.sqrt(p_c * (1 - p_c) / n_c + p_t * (1 - p_t) / n_t)

        if se_pooled == 0:
            z_stat = 0.0
            p_value = 1.0
        else:
            z_stat = effect / se_pooled
            p_value = 2 * (1 - _normal_cdf(abs(z_stat)))

        z_crit = _normal_ppf(1 - alpha / 2)
        ci_lower = effect - z_crit * se_effect
        ci_upper = effect + z_crit * se_effect

        # Cohen's h for effect size
        cohens_h = 2 * (math.asin(math.sqrt(p_t)) - math.asin(math.sqrt(p_c)))
        relative_effect = effect / p_c if p_c > 0 else float("inf")

    elif metric_type == "continuous":
        # Welch's t-test
        mean_c = sum(control_data) / n_c
        mean_t = sum(treatment_data) / n_t
        effect = mean_t - mean_c

        var_c = sum((x - mean_c) ** 2 for x in control_data) / max(n_c - 1, 1)
        var_t = sum((x - mean_t) ** 2 for x in treatment_data) / max(n_t - 1, 1)

        se = math.sqrt(var_c / n_c + var_t / n_t)

        if se == 0:
            t_stat = 0.0
            p_value = 1.0
        else:
            t_stat = effect / se
            # Approximate p-value using normal (good for large N)
            p_value = 2 * (1 - _normal_cdf(abs(t_stat)))

        z_crit = _normal_ppf(1 - alpha / 2)
        ci_lower = effect - z_crit * se
        ci_upper = effect + z_crit * se

        # Cohen's d
        pooled_sd = math.sqrt((var_c * (n_c - 1) + var_t * (n_t - 1)) / (n_c + n_t - 2))
        cohens_h = effect / pooled_sd if pooled_sd > 0 else 0.0
        z_stat = t_stat
        relative_effect = effect / mean_c if mean_c != 0 else float("inf")
    else:
        raise ValueError(f"Unknown metric_type: {metric_type}")

    return {
        "test_statistic": round(z_stat, 4),
        "p_value": round(p_value, 6),
        "ci_lower": round(ci_lower, 6),
        "ci_upper": round(ci_upper, 6),
        "effect_size": round(effect, 6),
        "relative_effect": round(relative_effect, 4),
        "cohens_d_or_h": round(cohens_h, 4),
        "significant": p_value < alpha,
        "alpha": alpha,
        "n_control": n_c,
        "n_treatment": n_t,
    }


def check_srm(observed_counts, expected_ratios=None):
    """Check for Sample Ratio Mismatch using chi-squared test.

    Args:
        observed_counts: list of observed sample sizes per variant
        expected_ratios: list of expected allocation ratios (default: equal)

    Returns:
        dict with 'chi2', 'p_value', 'alert' (bool), 'observed', 'expected'
    """
    k = len(observed_counts)
    total = sum(observed_counts)

    if expected_ratios is None:
        expected_ratios = [1.0 / k] * k

    # Normalize ratios
    ratio_sum = sum(expected_ratios)
    expected_ratios = [r / ratio_sum for r in expected_ratios]
    expected_counts = [total * r for r in expected_ratios]

    chi2 = sum((o - e) ** 2 / e for o, e in zip(observed_counts, expected_counts)
               if e > 0)

    # Chi-squared p-value approximation (df = k - 1)
    # For df=1 (two variants), use normal approximation
    df = k - 1
    if df == 1:
        p_value = 2 * (1 - _normal_cdf(math.sqrt(chi2)))
    else:
        # Wilson-Hilferty approximation for chi-squared CDF
        z = ((chi2 / df) ** (1 / 3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
        p_value = 1 - _normal_cdf(z)

    return {
        "chi2": round(chi2, 4),
        "p_value": round(p_value, 6),
        "alert": p_value < 0.001,
        "observed": observed_counts,
        "expected": [round(e, 1) for e in expected_counts],
    }


# --- Bayesian Testing ---

def run_bayesian_test(control_data, treatment_data, metric_type="proportion",
                      prior=None, n_samples=50000):
    """Run Bayesian A/B test with posterior sampling.

    Args:
        control_data: list of values for control group
        treatment_data: list of values for treatment group
        metric_type: 'proportion' or 'continuous'
        prior: dict with prior parameters (default: weakly informative)
            - For proportions: {'alpha': 1, 'beta': 1} (Beta prior)
            - For continuous: {'mu': 0, 'sigma': 1000} (Normal prior on mean)
        n_samples: number of Monte Carlo samples

    Returns:
        dict with 'prob_treatment_better', 'expected_loss',
        'credible_interval', 'posterior_control', 'posterior_treatment',
        'lift_distribution'
    """
    if metric_type == "proportion":
        return _bayesian_proportion(control_data, treatment_data, prior, n_samples)
    elif metric_type == "continuous":
        return _bayesian_continuous(control_data, treatment_data, prior, n_samples)
    else:
        raise ValueError(f"Unknown metric_type: {metric_type}")


def _bayesian_proportion(control_data, treatment_data, prior, n_samples):
    """Bayesian A/B test for proportions using Beta-Binomial model."""
    # Default prior: Beta(1, 1) = Uniform
    a0 = prior.get("alpha", 1) if prior else 1
    b0 = prior.get("beta", 1) if prior else 1

    # Sufficient statistics
    s_c = sum(control_data)
    n_c = len(control_data)
    s_t = sum(treatment_data)
    n_t = len(treatment_data)

    # Posterior parameters: Beta(a0 + successes, b0 + failures)
    a_c, b_c = a0 + s_c, b0 + (n_c - s_c)
    a_t, b_t = a0 + s_t, b0 + (n_t - s_t)

    # Monte Carlo sampling from Beta posteriors
    random.seed(42)
    samples_c = [_sample_beta(a_c, b_c) for _ in range(n_samples)]
    samples_t = [_sample_beta(a_t, b_t) for _ in range(n_samples)]

    # Compute metrics from samples
    lift_samples = [t - c for t, c in zip(samples_t, samples_c)]
    prob_better = sum(1 for l in lift_samples if l > 0) / n_samples
    expected_loss = sum(max(-l, 0) for l in lift_samples) / n_samples

    lift_sorted = sorted(lift_samples)
    ci_lo = lift_sorted[int(0.025 * n_samples)]
    ci_hi = lift_sorted[int(0.975 * n_samples)]

    mean_c = sum(samples_c) / n_samples
    mean_t = sum(samples_t) / n_samples

    return {
        "prob_treatment_better": round(prob_better, 4),
        "expected_loss": round(expected_loss, 6),
        "credible_interval": [round(ci_lo, 6), round(ci_hi, 6)],
        "lift_mean": round(sum(lift_samples) / n_samples, 6),
        "posterior_control": {
            "mean": round(mean_c, 6),
            "params": {"alpha": a_c, "beta": b_c},
        },
        "posterior_treatment": {
            "mean": round(mean_t, 6),
            "params": {"alpha": a_t, "beta": b_t},
        },
        "metric_type": "proportion",
        "prior": {"alpha": a0, "beta": b0},
        "n_samples": n_samples,
    }


def _bayesian_continuous(control_data, treatment_data, prior, n_samples):
    """Bayesian A/B test for continuous metrics using Normal model."""
    # Compute sufficient statistics
    n_c = len(control_data)
    n_t = len(treatment_data)
    mean_c = sum(control_data) / n_c
    mean_t = sum(treatment_data) / n_t
    var_c = sum((x - mean_c) ** 2 for x in control_data) / max(n_c - 1, 1)
    var_t = sum((x - mean_t) ** 2 for x in treatment_data) / max(n_t - 1, 1)

    # Posterior: Normal(sample_mean, sample_var / n) — with known-variance approx
    se_c = math.sqrt(var_c / n_c)
    se_t = math.sqrt(var_t / n_t)

    # Monte Carlo sampling
    random.seed(42)
    samples_c = [random.gauss(mean_c, se_c) for _ in range(n_samples)]
    samples_t = [random.gauss(mean_t, se_t) for _ in range(n_samples)]

    lift_samples = [t - c for t, c in zip(samples_t, samples_c)]
    prob_better = sum(1 for l in lift_samples if l > 0) / n_samples
    expected_loss = sum(max(-l, 0) for l in lift_samples) / n_samples

    lift_sorted = sorted(lift_samples)
    ci_lo = lift_sorted[int(0.025 * n_samples)]
    ci_hi = lift_sorted[int(0.975 * n_samples)]

    return {
        "prob_treatment_better": round(prob_better, 4),
        "expected_loss": round(expected_loss, 6),
        "credible_interval": [round(ci_lo, 6), round(ci_hi, 6)],
        "lift_mean": round(sum(lift_samples) / n_samples, 6),
        "posterior_control": {
            "mean": round(mean_c, 6),
            "std": round(se_c, 6),
        },
        "posterior_treatment": {
            "mean": round(mean_t, 6),
            "std": round(se_t, 6),
        },
        "metric_type": "continuous",
        "n_samples": n_samples,
    }


def _sample_beta(a, b):
    """Sample from Beta(a, b) using Gamma sampling.

    Beta(a, b) = Gamma(a, 1) / (Gamma(a, 1) + Gamma(b, 1))
    """
    x = random.gammavariate(a, 1)
    y = random.gammavariate(b, 1)
    return x / (x + y) if (x + y) > 0 else 0.5


# --- Uplift / Effect Size ---

def compute_uplift(control_data, treatment_data, metric_type="proportion"):
    """Compute uplift (treatment effect) with confidence intervals.

    Args:
        control_data: list of control group values
        treatment_data: list of treatment group values
        metric_type: 'proportion' or 'continuous'

    Returns:
        dict with 'absolute_uplift', 'relative_uplift', 'ci_lower', 'ci_upper'
    """
    n_c = len(control_data)
    n_t = len(treatment_data)

    if metric_type == "proportion":
        p_c = sum(control_data) / n_c
        p_t = sum(treatment_data) / n_t
        absolute = p_t - p_c
        relative = absolute / p_c if p_c > 0 else float("inf")
        se = math.sqrt(p_c * (1 - p_c) / n_c + p_t * (1 - p_t) / n_t)
    elif metric_type == "continuous":
        mean_c = sum(control_data) / n_c
        mean_t = sum(treatment_data) / n_t
        absolute = mean_t - mean_c
        relative = absolute / mean_c if mean_c != 0 else float("inf")
        var_c = sum((x - mean_c) ** 2 for x in control_data) / max(n_c - 1, 1)
        var_t = sum((x - mean_t) ** 2 for x in treatment_data) / max(n_t - 1, 1)
        se = math.sqrt(var_c / n_c + var_t / n_t)
    else:
        raise ValueError(f"Unknown metric_type: {metric_type}")

    z_crit = _normal_ppf(0.975)
    ci_lower = absolute - z_crit * se
    ci_upper = absolute + z_crit * se

    return {
        "absolute_uplift": round(absolute, 6),
        "relative_uplift": round(relative, 4),
        "ci_lower": round(ci_lower, 6),
        "ci_upper": round(ci_upper, 6),
        "standard_error": round(se, 6),
    }


# --- Causal Inference ---

def estimate_causal_impact(treated_pre, treated_post, control_pre, control_post,
                           method="did"):
    """Estimate causal impact using difference-in-differences or related methods.

    Args:
        treated_pre: list of outcome values for treated group, pre-treatment
        treated_post: list of outcome values for treated group, post-treatment
        control_pre: list of outcome values for control group, pre-treatment
        control_post: list of outcome values for control group, post-treatment
        method: 'did' (difference-in-differences) or 'psm' (propensity-adjusted)

    Returns:
        dict with 'effect', 'std_error', 'ci_lower', 'ci_upper', 'p_value',
        'parallel_trends_test'
    """
    if method == "did":
        return _did_estimator(treated_pre, treated_post, control_pre, control_post)
    elif method == "psm":
        # PSM reduces to DiD after matching — pass through
        return _did_estimator(treated_pre, treated_post, control_pre, control_post)
    else:
        raise ValueError(f"Unknown method: {method}. Use 'did' or 'psm'.")


def _did_estimator(treated_pre, treated_post, control_pre, control_post):
    """Difference-in-differences estimator."""
    mean_tp = sum(treated_post) / len(treated_post)
    mean_tr = sum(treated_pre) / len(treated_pre)
    mean_cp = sum(control_post) / len(control_post)
    mean_cr = sum(control_pre) / len(control_pre)

    # DiD estimate
    did_effect = (mean_tp - mean_tr) - (mean_cp - mean_cr)

    # Standard error (assuming independent groups)
    n_tp, n_tr = len(treated_post), len(treated_pre)
    n_cp, n_cr = len(control_post), len(control_pre)

    var_tp = sum((x - mean_tp) ** 2 for x in treated_post) / max(n_tp - 1, 1)
    var_tr = sum((x - mean_tr) ** 2 for x in treated_pre) / max(n_tr - 1, 1)
    var_cp = sum((x - mean_cp) ** 2 for x in control_post) / max(n_cp - 1, 1)
    var_cr = sum((x - mean_cr) ** 2 for x in control_pre) / max(n_cr - 1, 1)

    se = math.sqrt(var_tp / n_tp + var_tr / n_tr + var_cp / n_cp + var_cr / n_cr)

    # Test statistic and p-value
    if se > 0:
        z = did_effect / se
        p_value = 2 * (1 - _normal_cdf(abs(z)))
    else:
        z = 0.0
        p_value = 1.0

    z_crit = _normal_ppf(0.975)
    ci_lower = did_effect - z_crit * se
    ci_upper = did_effect + z_crit * se

    # Parallel trends test: compare pre-period trends
    # (simplified: test if pre-period means are similar in trajectory)
    pre_diff = mean_tr - mean_cr
    parallel_trends = {
        "pre_treatment_diff": round(pre_diff, 6),
        "note": "Formal parallel trends test requires multiple pre-periods",
    }

    return {
        "effect": round(did_effect, 6),
        "std_error": round(se, 6),
        "ci_lower": round(ci_lower, 6),
        "ci_upper": round(ci_upper, 6),
        "p_value": round(p_value, 6),
        "test_statistic": round(z, 4),
        "method": "difference-in-differences",
        "group_means": {
            "treated_pre": round(mean_tr, 6),
            "treated_post": round(mean_tp, 6),
            "control_pre": round(mean_cr, 6),
            "control_post": round(mean_cp, 6),
        },
        "parallel_trends_test": parallel_trends,
    }


# --- Multiple Comparison Corrections ---

def bonferroni_correction(p_values, alpha=0.05):
    """Apply Bonferroni correction for multiple comparisons.

    Args:
        p_values: list of raw p-values
        alpha: family-wise error rate

    Returns:
        dict with 'adjusted_p_values', 'adjusted_alpha', 'significant'
    """
    m = len(p_values)
    adjusted_alpha = alpha / m
    adjusted = [min(p * m, 1.0) for p in p_values]

    return {
        "adjusted_p_values": [round(p, 6) for p in adjusted],
        "adjusted_alpha": round(adjusted_alpha, 6),
        "significant": [p < alpha for p in adjusted],
    }


def benjamini_hochberg(p_values, alpha=0.05):
    """Apply Benjamini-Hochberg procedure for FDR control.

    Args:
        p_values: list of raw p-values
        alpha: false discovery rate threshold

    Returns:
        dict with 'adjusted_p_values', 'significant', 'num_discoveries'
    """
    m = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])

    adjusted = [0.0] * m
    significant = [False] * m

    # Step-up procedure
    prev_adj = 1.0
    for rank_idx in range(m - 1, -1, -1):
        orig_idx, p = indexed[rank_idx]
        rank = rank_idx + 1
        adj_p = min(p * m / rank, prev_adj, 1.0)
        adjusted[orig_idx] = adj_p
        significant[orig_idx] = adj_p < alpha
        prev_adj = adj_p

    return {
        "adjusted_p_values": [round(p, 6) for p in adjusted],
        "significant": significant,
        "num_discoveries": sum(significant),
    }


# --- Utility Functions ---

def summarize_experiment_data(data, group_col="variant", metric_col="converted"):
    """Compute summary statistics for experiment data.

    Args:
        data: list of dicts (rows) with group and metric columns
        group_col: column name for variant assignment
        metric_col: column name for the metric

    Returns:
        dict with per-group summaries and overall stats
    """
    groups = {}
    for row in data:
        group = row.get(group_col, "unknown")
        value = row.get(metric_col, 0)
        if group not in groups:
            groups[group] = []
        groups[group].append(value)

    summaries = {}
    for group, values in groups.items():
        n = len(values)
        mean = sum(values) / n if n > 0 else 0
        variance = sum((x - mean) ** 2 for x in values) / max(n - 1, 1) if n > 1 else 0
        summaries[group] = {
            "n": n,
            "mean": round(mean, 6),
            "std": round(math.sqrt(variance), 6),
            "min": round(min(values), 6) if values else None,
            "max": round(max(values), 6) if values else None,
            "sum": round(sum(values), 6),
        }

    return {
        "groups": summaries,
        "total_n": sum(s["n"] for s in summaries.values()),
        "group_count": len(summaries),
    }
