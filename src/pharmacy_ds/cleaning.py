"""Auditable Pandas cleaning; keep raw data immutable and never impute outcomes."""

from typing import Any

import numpy as np
import pandas as pd

from pharmacy_ds.config import (
    IMPUTE_COLUMNS,
    INTEGER_COLUMNS,
    NUMERIC_COLUMNS,
    RAW_COLUMNS,
    RISK_LEVELS,
    WORKFLOWS,
)


class DataValidationError(ValueError):
    """Raised when input data cannot satisfy the documented contract."""


def require_columns(df: pd.DataFrame) -> None:
    """Reject a missing schema before any transformations."""
    missing = sorted(set(RAW_COLUMNS) - set(df.columns))
    if missing:
        raise DataValidationError(f"Missing required columns: {', '.join(missing)}")


def clean_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Return a validated table, rejected rows and a machine-readable audit.

    Exact duplicate records are removed. Invalid ID, date or workflow rows are
    quarantined. Noncritical numeric defects become missing; predictors receive
    flagged median imputation. Missing wait outcomes remain missing.
    """
    require_columns(raw)
    audit: dict[str, Any] = {
        "input_rows": len(raw),
        "input_missing_by_column": {c: int(raw[c].isna().sum()) for c in RAW_COLUMNS},
        "exact_duplicates_removed": int(raw.duplicated(subset=RAW_COLUMNS).sum()),
    }
    df = raw.drop_duplicates(subset=RAW_COLUMNS).copy()
    df["raw_csv_row"] = df.index.to_numpy() + 2
    df["pharmacy_id"] = df["pharmacy_id"].astype("string").str.strip().str.upper()
    workflow_map = {w.lower(): w for w in WORKFLOWS}
    df["workflow"] = (
        df["workflow"].astype("string").str.strip().str.lower().map(workflow_map)
    )
    df["report_date"] = pd.to_datetime(
        df["report_date"], format="%Y-%m-%d", errors="coerce"
    )
    invalid_id = ~df["pharmacy_id"].str.fullmatch(r"PH\d{3}", na=False)
    invalid_workflow = df["workflow"].isna()
    invalid_date = df["report_date"].isna()
    reasons = pd.Series("", index=df.index, dtype="string")
    for mask, label in [
        (invalid_id, "invalid pharmacy_id; "),
        (invalid_workflow, "invalid workflow; "),
        (invalid_date, "invalid report_date; "),
    ]:
        reasons.loc[mask] = reasons.loc[mask] + label
    rejected_mask = invalid_id | invalid_workflow | invalid_date
    rejected = raw.loc[df.index[rejected_mask]].copy()
    rejected["raw_csv_row"] = rejected.index.to_numpy() + 2
    rejected["rejection_reason"] = reasons.loc[rejected_mask].str.rstrip("; ")
    df = df.loc[~rejected_mask].copy()
    if df.empty:
        raise DataValidationError("No usable rows remain after critical validation.")
    if df["pharmacy_id"].duplicated().any():
        raise DataValidationError(
            "Conflicting pharmacy_id values remain after exact deduplication."
        )
    audit["rows_after_exact_deduplication"] = len(df) + len(rejected)
    audit["critical_rows_rejected"] = len(rejected)
    audit["rejections_by_reason"] = {
        "invalid_id": int(invalid_id.sum()),
        "invalid_workflow": int(invalid_workflow.sum()),
        "invalid_date": int(invalid_date.sum()),
    }
    allowed_regions = {v.lower(): v for v in ["Hyderabad", "Warangal", "Nalgonda"]}
    df["region"] = (
        df["region"]
        .astype("string")
        .str.strip()
        .str.lower()
        .map(allowed_regions)
        .fillna("Unknown")
    )
    df["pharmacy_type"] = (
        df["pharmacy_type"]
        .astype("string")
        .str.strip()
        .str.title()
        .where(lambda s: s.isin(["Community", "Hospital"]), "Unknown")
    )
    audit["unknown_region_count"] = int(df["region"].eq("Unknown").sum())
    audit["invalid_numeric_values_converted"] = {}
    for col in NUMERIC_COLUMNS:
        before_present = df[col].notna()
        values = pd.to_numeric(df[col], errors="coerce").replace(
            [np.inf, -np.inf], np.nan
        )
        if col in INTEGER_COLUMNS:
            minimum = 1 if col == "staff_on_duty" else 0
            valid = values.ge(minimum) & values.mod(1).eq(0)
        elif col == "stock_availability_pct":
            valid = values.between(0, 100)
        elif col == "mean_wait_minutes":
            valid = values.gt(0)
        else:
            valid = values.ge(0)
        df[col] = values.where(valid)
        audit["invalid_numeric_values_converted"][col] = int(
            (before_present & df[col].isna()).sum()
        )
    audit["imputed_counts"] = {}
    audit["imputation_values"] = {}
    for col in IMPUTE_COLUMNS:
        flag = df[col].isna()
        if df[col].notna().sum() == 0:
            raise DataValidationError(
                f"Cannot estimate a median: {col} has no valid observations."
            )
        median = float(df[col].median())
        fill_value = int(round(median)) if col in INTEGER_COLUMNS else round(median, 2)
        df[f"{col}_was_imputed"] = flag
        df[col] = df[col].fillna(fill_value)
        if col in INTEGER_COLUMNS:
            df[col] = df[col].astype("int64")
        audit["imputed_counts"][col] = int(flag.sum())
        audit["imputation_values"][col] = fill_value
    df["mean_wait_minutes_missing"] = df["mean_wait_minutes"].isna()
    df["workload_per_staff"] = df["daily_prescriptions"] / df["staff_on_duty"]
    df["stock_risk"] = pd.Categorical(
        np.select(
            [df["stock_availability_pct"].ge(95), df["stock_availability_pct"].ge(90)],
            ["Low", "Medium"],
            default="High",
        ),
        categories=RISK_LEVELS,
        ordered=True,
    )
    for col in ["region", "pharmacy_type", "workflow"]:
        df[col] = df[col].astype("category")
    df["notes"] = df["notes"].astype("string").str.strip().fillna("")
    df = df.reset_index(drop=True)
    audit["output_rows"] = len(df)
    audit["missing_wait_outcomes_retained"] = int(df["mean_wait_minutes"].isna().sum())
    audit["observed_wait_outcomes"] = int(df["mean_wait_minutes"].notna().sum())
    validate_clean_data(df)
    return df, rejected.reset_index(drop=True), audit


def validate_clean_data(df: pd.DataFrame) -> None:
    """Fail loudly on integrity errors; use explicit checks, not removable asserts."""
    require_columns(df)
    if df.empty:
        raise DataValidationError("Clean data is empty.")
    if not df["pharmacy_id"].astype("string").str.fullmatch(r"PH\d{3}", na=False).all():
        raise DataValidationError("pharmacy_id must match PH followed by three digits.")
    if df["pharmacy_id"].duplicated().any():
        raise DataValidationError("pharmacy_id must be unique.")
    if df["report_date"].isna().any():
        raise DataValidationError("report_date cannot be missing.")
    if not df["workflow"].isin(WORKFLOWS).all():
        raise DataValidationError("workflow has an invalid category.")
    for col in IMPUTE_COLUMNS:
        vals = pd.to_numeric(df[col], errors="coerce")
        if vals.isna().any() or not np.isfinite(vals.to_numpy(dtype=float)).all():
            raise DataValidationError(
                f"{col} must contain finite, non-missing numbers."
            )
        if (vals < 0).any():
            raise DataValidationError(f"{col} cannot contain negative values.")
        if col in INTEGER_COLUMNS and not vals.mod(1).eq(0).all():
            raise DataValidationError(f"{col} must contain whole numbers.")
    if not df["staff_on_duty"].gt(0).all():
        raise DataValidationError("staff_on_duty must be positive.")
    if not df["stock_availability_pct"].between(0, 100).all():
        raise DataValidationError("stock_availability_pct must be between 0 and 100.")
    observed_wait = pd.to_numeric(df["mean_wait_minutes"].dropna(), errors="coerce")
    if (
        observed_wait.isna().any()
        or not np.isfinite(observed_wait).all()
        or not observed_wait.gt(0).all()
    ):
        raise DataValidationError(
            "Observed mean_wait_minutes must be finite and positive."
        )
    expected_risk = np.select(
        [df["stock_availability_pct"].ge(95), df["stock_availability_pct"].ge(90)],
        ["Low", "Medium"],
        default="High",
    )
    if not np.array_equal(df["stock_risk"].astype(str).to_numpy(), expected_risk):
        raise DataValidationError(
            "stock_risk is inconsistent with its documented thresholds."
        )
    expected_workload = df["daily_prescriptions"] / df["staff_on_duty"]
    if not np.allclose(df["workload_per_staff"], expected_workload):
        raise DataValidationError("workload_per_staff is inconsistent with its inputs.")


def load_cleaned(path) -> pd.DataFrame:
    """Restore CSV types (CSV itself does not preserve category or datetime metadata)."""
    df = pd.read_csv(path, parse_dates=["report_date"])
    for col in ["region", "pharmacy_type", "workflow"]:
        df[col] = df[col].astype("category")
    df["stock_risk"] = pd.Categorical(
        df["stock_risk"], categories=RISK_LEVELS, ordered=True
    )
    df["pharmacy_id"] = df["pharmacy_id"].astype("string")
    df["notes"] = df["notes"].astype("string")
    for col in [
        c for c in df.columns if c.endswith("_was_imputed") or c.endswith("_missing")
    ]:
        if df[col].dtype != bool:
            mapped = (
                df[col].astype("string").str.lower().map({"true": True, "false": False})
            )
            if mapped.isna().any():
                raise DataValidationError(f"Invalid Boolean flag in {col}.")
            df[col] = mapped.astype(bool)
    validate_clean_data(df)
    return df
