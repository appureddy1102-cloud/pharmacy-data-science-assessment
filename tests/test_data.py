"""Schema, corruption handling, auditability and CSV round-trip tests."""

import numpy as np
import pandas as pd
import pytest

from pharmacy_ds.cleaning import (
    DataValidationError,
    clean_data,
    load_cleaned,
    validate_clean_data,
)
from pharmacy_ds.config import IMPUTE_COLUMNS, INTEGER_COLUMNS, RAW_COLUMNS, RISK_LEVELS
from pharmacy_ds.generate import generate_sample_data


def test_generator_is_repeatable(tmp_path):
    a = generate_sample_data(tmp_path / "a.csv")
    b = generate_sample_data(tmp_path / "b.csv")
    pd.testing.assert_frame_equal(a, b)


def test_raw_shape_and_duplicates(raw):
    assert raw.shape == (125, 13)
    assert raw.duplicated().sum() == 5


def test_raw_data_remains_unchanged(raw):
    original = raw.copy(deep=True)
    clean_data(raw)
    pd.testing.assert_frame_equal(raw, original)


def test_clean_shape_and_rejection_accounting(cleaned):
    df, rejected, audit = cleaned
    assert len(df) == 117
    assert len(rejected) == 3
    assert (
        len(df) + len(rejected) + audit["exact_duplicates_removed"]
        == audit["input_rows"]
    )


def test_rejection_reasons(cleaned):
    _, rejected, audit = cleaned
    assert audit["rejections_by_reason"] == {
        "invalid_id": 1,
        "invalid_workflow": 1,
        "invalid_date": 1,
    }
    assert set(rejected["rejection_reason"]) == {
        "invalid pharmacy_id",
        "invalid workflow",
        "invalid report_date",
    }
    assert rejected["raw_csv_row"].tolist() == [2, 3, 4]


@pytest.mark.parametrize("column", RAW_COLUMNS)
def test_required_columns_are_enforced(raw, column):
    with pytest.raises(DataValidationError, match="Missing required columns"):
        clean_data(raw.drop(columns=column))


def test_unique_ids_and_original_row_trace(cleaned):
    df, _, _ = cleaned
    assert df["pharmacy_id"].is_unique
    assert df["raw_csv_row"].is_unique


def test_outcomes_are_never_imputed(cleaned):
    df, _, audit = cleaned
    assert df["mean_wait_minutes"].isna().sum() == 6
    assert audit["observed_wait_outcomes"] == 111
    assert "mean_wait_minutes" not in audit["imputed_counts"]
    pd.testing.assert_series_equal(
        df["mean_wait_minutes"].isna(),
        df["mean_wait_minutes_missing"],
        check_names=False,
    )


@pytest.mark.parametrize("column", IMPUTE_COLUMNS)
def test_imputation_flags_and_medians(cleaned, column):
    df, _, audit = cleaned
    flags = df[f"{column}_was_imputed"]
    assert flags.dtype == bool
    assert int(flags.sum()) == audit["imputed_counts"][column]
    assert df[column].notna().all()
    assert (df.loc[flags, column] == audit["imputation_values"][column]).all()


@pytest.mark.parametrize("column", INTEGER_COLUMNS)
def test_count_columns_are_whole_and_nonnegative(cleaned, column):
    df, _, _ = cleaned
    assert df[column].mod(1).eq(0).all()
    assert df[column].ge(0).all()


def test_categorical_order_and_known_ranges(cleaned):
    df, _, _ = cleaned
    assert df["stock_risk"].cat.categories.tolist() == RISK_LEVELS
    assert df["stock_risk"].cat.ordered
    assert df["stock_availability_pct"].between(0, 100).all()
    assert df["staff_on_duty"].gt(0).all()


def test_invalid_number_counts(cleaned):
    _, _, audit = cleaned
    invalid = audit["invalid_numeric_values_converted"]
    assert invalid["daily_prescriptions"] == 2
    assert invalid["staff_on_duty"] == 1
    assert invalid["mean_wait_minutes"] == 1
    assert invalid["stock_availability_pct"] == 1
    assert invalid["inventory_value_inr"] == 1


def test_conflicting_ids_are_not_silently_dropped(raw):
    raw.loc[4, "pharmacy_id"] = raw.loc[3, "pharmacy_id"]
    with pytest.raises(DataValidationError, match="Conflicting pharmacy_id"):
        clean_data(raw)


def test_no_valid_rows_fails(raw):
    raw["workflow"] = "invalid"
    with pytest.raises(DataValidationError, match="No usable rows"):
        clean_data(raw)


def test_no_median_donor_fails(raw):
    raw["inventory_value_inr"] = np.nan
    with pytest.raises(DataValidationError, match="Cannot estimate a median"):
        clean_data(raw)


@pytest.mark.parametrize(
    "column", ["inventory_value_inr", "mean_wait_minutes", "stock_availability_pct"]
)
def test_infinite_numbers_are_not_allowed(raw, column):
    raw.loc[24, column] = np.inf
    df, _, _ = clean_data(raw)
    assert np.isfinite(df[column].dropna()).all()
    if column == "mean_wait_minutes":
        assert pd.isna(df.loc[df["pharmacy_id"].eq("PH025"), column]).all()
    else:
        assert df.loc[df["pharmacy_id"].eq("PH025"), f"{column}_was_imputed"].all()


def test_csv_round_trip_restores_types(cleaned, tmp_path):
    df, _, _ = cleaned
    path = tmp_path / "clean.csv"
    df.to_csv(path, index=False)
    restored = load_cleaned(path)
    assert restored["stock_risk"].cat.ordered
    assert str(restored["report_date"].dtype).startswith("datetime64")
    assert restored["staff_on_duty_was_imputed"].dtype == bool
    assert len(restored) == len(df)


def test_validation_rejects_duplicate_id(cleaned):
    df, _, _ = cleaned
    df.loc[1, "pharmacy_id"] = df.loc[0, "pharmacy_id"]
    with pytest.raises(DataValidationError, match="unique"):
        validate_clean_data(df)


def test_validation_rejects_invalid_stock_range(cleaned):
    df, _, _ = cleaned
    df.loc[0, "stock_availability_pct"] = 101
    with pytest.raises(DataValidationError, match="between 0 and 100"):
        validate_clean_data(df)


def test_validation_rejects_inconsistent_derived_data(cleaned):
    df, _, _ = cleaned
    df.loc[0, "workload_per_staff"] += 1
    with pytest.raises(DataValidationError, match="workload_per_staff is inconsistent"):
        validate_clean_data(df)
