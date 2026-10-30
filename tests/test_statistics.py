"""Independently verify calculations, denominators and CI sign conventions."""

import json

import numpy as np
import pytest
from scipy import stats

from pharmacy_ds.statistics import analyze, correlation_sample


def test_descriptive_statistics_match_numpy(cleaned):
    df, _, _ = cleaned
    result = analyze(df)
    y = df["mean_wait_minutes"].dropna().to_numpy()
    assert result["wait"]["mean"] == pytest.approx(np.mean(y))
    assert result["wait"]["sample_variance"] == pytest.approx(np.var(y, ddof=1))
    assert result["wait"]["sample_sd"] == pytest.approx(np.std(y, ddof=1))


def test_welch_and_ci_match_scipy(cleaned):
    df, _, _ = cleaned
    result = analyze(df)["welch_test"]
    a = df.loc[df["workflow"].eq("Standard"), "mean_wait_minutes"].dropna()
    b = df.loc[df["workflow"].eq("Barcode-assisted"), "mean_wait_minutes"].dropna()
    independent = stats.ttest_ind(a, b, equal_var=False)
    ci = independent.confidence_interval(confidence_level=0.95)
    assert result["t_statistic"] == pytest.approx(independent.statistic)
    assert result["p_value"] == pytest.approx(independent.pvalue)
    assert result["degrees_of_freedom"] == pytest.approx(independent.df)
    assert result["ci95_low"] == pytest.approx(ci.low)
    assert result["ci95_high"] == pytest.approx(ci.high)
    assert result["difference_minutes"] == pytest.approx(a.mean() - b.mean())


def test_group_denominators_match_observed_outcomes(cleaned):
    df, _, audit = cleaned
    result = analyze(df)
    assert (
        sum(g["n"] for g in result["workflow_summary"].values())
        == audit["observed_wait_outcomes"]
    )
    assert sum(g["missing_outcomes"] for g in result["workflow_summary"].values()) == 6


def test_correlation_sample_excludes_imputations(cleaned):
    df, _, _ = cleaned
    sample = correlation_sample(df)
    expected = df.loc[
        df["mean_wait_minutes"].notna()
        & ~df["daily_prescriptions_was_imputed"]
        & ~df["staff_on_duty_was_imputed"]
    ]
    assert len(sample) == len(expected)
    assert sample["mean_wait_minutes"].notna().all()
    result = analyze(df)["correlation"]
    assert result["pearson_r"] == pytest.approx(
        sample["workload_per_staff"].corr(sample["mean_wait_minutes"])
    )
    assert result["sample_covariance"] == pytest.approx(
        sample["workload_per_staff"].cov(sample["mean_wait_minutes"])
    )


def test_probability_has_the_correct_denominator(cleaned):
    df, _, _ = cleaned
    result = analyze(df)["probability"]
    y = df["mean_wait_minutes"].dropna()
    assert result["observed_n"] == len(y)
    assert result["empirical_probability"] == pytest.approx(y.lt(10).mean())
    assert 0 <= result["empirical_probability"] <= 1


def test_json_is_strict_and_finite(cleaned):
    result = analyze(cleaned[0])
    encoded = json.dumps(result, allow_nan=False)
    assert "NaN" not in encoded


def test_tiny_sample_fails(cleaned):
    with pytest.raises(ValueError, match="At least three"):
        analyze(cleaned[0].iloc[:2])


def test_hand_calculable_variance():
    values = np.array([2, 4, 4, 4, 5, 5, 7, 9])
    assert values.mean() == 5
    assert np.var(values, ddof=0) == 4
    assert np.var(values, ddof=1) == pytest.approx(32 / 7)
