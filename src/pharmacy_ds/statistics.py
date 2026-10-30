"""Descriptive analysis and a prespecified independent-samples Welch test."""

import numpy as np
import pandas as pd
from scipy import stats

from pharmacy_ds.config import WORKFLOWS


def correlation_sample(df: pd.DataFrame) -> pd.DataFrame:
    """Use observed outcomes AND observed workload inputs, not median-filled inputs."""
    mask = (
        df["mean_wait_minutes"].notna()
        & ~df["daily_prescriptions_was_imputed"]
        & ~df["staff_on_duty_was_imputed"]
    )
    return df.loc[mask, ["workload_per_staff", "mean_wait_minutes", "workflow"]].copy()


def analyze(df: pd.DataFrame) -> dict:
    """Return JSON-safe real calculations; the statistical unit is one pharmacy."""
    y = df["mean_wait_minutes"].dropna().astype(float)
    if len(y) < 3:
        raise ValueError("At least three observed wait outcomes are required.")
    groups = {}
    arrays = []
    for workflow in WORKFLOWS:
        values = (
            df.loc[df["workflow"].eq(workflow), "mean_wait_minutes"]
            .dropna()
            .astype(float)
            .to_numpy()
        )
        if len(values) < 3 or np.var(values, ddof=1) <= 0:
            raise ValueError(
                "Each workflow needs at least three nonconstant observed outcomes."
            )
        arrays.append(values)
        normality = stats.shapiro(values)
        groups[workflow] = {
            "n": len(values),
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "sample_sd": float(np.std(values, ddof=1)),
            "sample_variance": float(np.var(values, ddof=1)),
            "missing_outcomes": int(
                df.loc[df["workflow"].eq(workflow), "mean_wait_minutes"].isna().sum()
            ),
            "shapiro_w": float(normality.statistic),
            "shapiro_p": float(normality.pvalue),
        }
    a, b = arrays
    test = stats.ttest_ind(
        a, b, equal_var=False, alternative="two-sided", nan_policy="raise"
    )
    # Manual Welch-Satterthwaite formula, also checked against SciPy in tests.
    va, vb = np.var(a, ddof=1), np.var(b, ddof=1)
    qa, qb = va / len(a), vb / len(b)
    se = np.sqrt(qa + qb)
    degrees_freedom = (qa + qb) ** 2 / (qa**2 / (len(a) - 1) + qb**2 / (len(b) - 1))
    difference = float(np.mean(a) - np.mean(b))
    margin = float(stats.t.ppf(0.975, df=degrees_freedom) * se)
    observed = correlation_sample(df)
    if len(observed) < 3:
        raise ValueError(
            "At least three complete workload/wait observations are required."
        )
    covariance = float(
        np.cov(observed["workload_per_staff"], observed["mean_wait_minutes"], ddof=1)[
            0, 1
        ]
    )
    pearson = stats.pearsonr(
        observed["workload_per_staff"], observed["mean_wait_minutes"]
    )
    successes = int(y.lt(10).sum())
    return {
        "analysis_unit": "one fictional pharmacy; not an individual prescription",
        "clean_rows": len(df),
        "observed_wait_n": len(y),
        "wait": {
            "mean": float(y.mean()),
            "median": float(y.median()),
            "sample_variance": float(y.var(ddof=1)),
            "sample_sd": float(y.std(ddof=1)),
            "minimum": float(y.min()),
            "maximum": float(y.max()),
            "q1": float(y.quantile(0.25)),
            "q3": float(y.quantile(0.75)),
        },
        "staff_modes": [int(x) for x in df["staff_on_duty"].mode()],
        "staff_mode_includes_imputed_values": True,
        "workflow_summary": groups,
        "welch_test": {
            "comparison": "Standard minus Barcode-assisted",
            "alpha": 0.05,
            "alternative": "two-sided",
            "difference_minutes": difference,
            "standard_error": float(se),
            "t_statistic": float(test.statistic),
            "degrees_of_freedom": float(degrees_freedom),
            "p_value": float(test.pvalue),
            "ci95_low": difference - margin,
            "ci95_high": difference + margin,
            "decision": "Reject H0" if test.pvalue < 0.05 else "Do not reject H0",
        },
        "correlation": {
            "complete_observed_n": len(observed),
            "pearson_r": float(pearson.statistic),
            "sample_covariance": covariance,
            "covariance_units": "(prescriptions per staff member) * minutes",
        },
        "probability": {
            "event": "observed site mean wait below 10 minutes",
            "success_count": successes,
            "observed_n": len(y),
            "empirical_probability": successes / len(y),
        },
        "risk_counts": {
            str(k): int(v) for k, v in df["stock_risk"].value_counts(sort=False).items()
        },
        "normal_example": {
            "assumed_mean": 10,
            "assumed_sd": 2,
            "p_le_12": float(stats.norm.cdf(12, loc=10, scale=2)),
            "p_8_to_12": float(stats.norm.cdf(12, 10, 2) - stats.norm.cdf(8, 10, 2)),
        },
    }


def format_summary(result: dict) -> str:
    """Readable statistical output, also reused in the report and README."""
    w, t, c, p = (
        result["wait"],
        result["welch_test"],
        result["correlation"],
        result["probability"],
    )
    lines = [
        "SYNTHETIC PHARMACY OPERATIONS — EXECUTED RESULTS",
        f"Clean sites: {result['clean_rows']}; observed wait outcomes: {result['observed_wait_n']}",
        f"Wait mean = {w['mean']:.3f} min; median = {w['median']:.3f} min",
        f"Sample variance = {w['sample_variance']:.3f} min^2; sample SD = {w['sample_sd']:.3f} min",
    ]
    for name, group in result["workflow_summary"].items():
        lines.append(
            f"{name}: n={group['n']}, mean={group['mean']:.3f}, SD={group['sample_sd']:.3f} min"
        )
    lines.extend(
        [
            f"Welch difference (Standard - Barcode-assisted) = {t['difference_minutes']:.3f} min",
            f"95% CI = [{t['ci95_low']:.3f}, {t['ci95_high']:.3f}] min",
            f"t={t['t_statistic']:.4f}, df={t['degrees_of_freedom']:.3f}, p={t['p_value']:.6g}",
            f"At alpha=0.05: {t['decision']} (simulation only; not a clinical claim).",
            f"Workload vs wait: n={c['complete_observed_n']}, r={c['pearson_r']:.4f}, covariance={c['sample_covariance']:.4f}",
            f"P(site mean wait < 10 min | observed) = {p['success_count']}/{p['observed_n']} = {p['empirical_probability']:.4f}",
            "Missing wait outcomes were NOT imputed; correlation excludes imputed workload inputs.",
            "This dataset is fictional and its generating formula includes a workflow effect.",
        ]
    )
    return "\n".join(lines) + "\n"
