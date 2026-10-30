"""Generate fictional, independent pharmacy-level records and known defects.

No patient data, medicine doses or real business observations are used.
The outcome-generating formula deliberately includes a workflow difference;
therefore a statistical difference is an exercise, not empirical evidence.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from pharmacy_ds.config import SEED


def generate_sample_data(path: Path, seed: int = SEED) -> pd.DataFrame:
    """Write 120 fictional sites plus five exact duplicate rows to a CSV."""
    rng = np.random.default_rng(seed)
    n = 120
    workflow = rng.permutation(["Standard"] * 60 + ["Barcode-assisted"] * 60)
    prescriptions = rng.integers(65, 221, n)
    staff = rng.integers(2, 7, n)
    workload = prescriptions / staff
    wait = np.round(
        7.0
        + 0.035 * workload
        - 1.1 * (workflow == "Barcode-assisted")
        + rng.normal(0, 1.35, n),
        2,
    )
    stock = np.round(
        np.clip(
            94 + 0.5 * staff - 0.015 * prescriptions + rng.normal(0, 2.5, n), 75, 100
        ),
        2,
    )
    inventory = np.round(prescriptions * 210 + rng.uniform(1500, 11000, n), 2)
    risk = np.select([stock >= 95, stock >= 90], ["Low", "Medium"], default="High")
    df = pd.DataFrame(
        {
            "pharmacy_id": [f"PH{i:03d}" for i in range(1, n + 1)],
            "report_date": "2026-09-30",
            "region": rng.choice(["Hyderabad", "Warangal", "Nalgonda"], n),
            "pharmacy_type": rng.choice(["Community", "Hospital"], n, p=[0.75, 0.25]),
            "workflow": workflow,
            "daily_prescriptions": prescriptions.astype(float),
            "staff_on_duty": staff.astype(float),
            "mean_wait_minutes": wait,
            "stock_availability_pct": stock,
            "inventory_value_inr": inventory,
            "expired_units": rng.poisson(2, n).astype(float),
            "stock_risk": risk,
            "notes": rng.choice(
                [
                    "Routine stock check completed",
                    "Review reorder levels",
                    "Stock counts verified",
                    "Supplier delivery expected",
                ],
                n,
            ),
        }
    )
    # Three separate critical defects are quarantined, never guessed.
    df.loc[0, "pharmacy_id"] = None
    df.loc[1, "workflow"] = "unrecognized workflow"
    df.loc[2, "report_date"] = "not-a-date"
    # Noncritical missing values and invalid numbers are handled transparently.
    df.loc[[5, 12, 35, 74], "daily_prescriptions"] = np.nan
    df.loc[14, "daily_prescriptions"] = -15
    df.loc[20, "daily_prescriptions"] = 121.5
    df.loc[[6, 25, 58], "staff_on_duty"] = np.nan
    df.loc[17, "staff_on_duty"] = 0
    df.loc[[8, 29, 47, 83, 106], "mean_wait_minutes"] = np.nan
    df.loc[40, "mean_wait_minutes"] = -2
    df.loc[[9, 34, 80], "stock_availability_pct"] = np.nan
    df.loc[18, "stock_availability_pct"] = 135
    df.loc[[10, 66], "inventory_value_inr"] = np.nan
    df.loc[19, "inventory_value_inr"] = -500
    df.loc[[11, 55], "region"] = None
    df.loc[27, "region"] = "??"
    df.loc[13, "region"] = " nalgonda "
    df.loc[15, "workflow"] = " STANDARD "
    df.loc[16, "pharmacy_type"] = " hospital "
    dirty = pd.concat([df, df.loc[[30, 31, 32, 33, 36]]], ignore_index=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    dirty.to_csv(path, index=False)
    return dirty
