"""Project paths, reproducible seed and explicit data contracts."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SEED = 2026
WORKFLOWS = ["Standard", "Barcode-assisted"]
RISK_LEVELS = ["Low", "Medium", "High"]
RAW_COLUMNS = [
    "pharmacy_id",
    "report_date",
    "region",
    "pharmacy_type",
    "workflow",
    "daily_prescriptions",
    "staff_on_duty",
    "mean_wait_minutes",
    "stock_availability_pct",
    "inventory_value_inr",
    "expired_units",
    "stock_risk",
    "notes",
]
NUMERIC_COLUMNS = [
    "daily_prescriptions",
    "staff_on_duty",
    "mean_wait_minutes",
    "stock_availability_pct",
    "inventory_value_inr",
    "expired_units",
]
IMPUTE_COLUMNS = [c for c in NUMERIC_COLUMNS if c != "mean_wait_minutes"]
INTEGER_COLUMNS = ["daily_prescriptions", "staff_on_duty", "expired_units"]
