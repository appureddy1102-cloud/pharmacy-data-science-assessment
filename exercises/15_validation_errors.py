"""Task 15: deliberately break data and prove that validation rejects it."""

from pharmacy_ds.cleaning import DataValidationError, load_cleaned, validate_clean_data
from pharmacy_ds.config import PROJECT_ROOT

df = load_cleaned(PROJECT_ROOT / "data/processed/pharmacy_operations_clean.csv")
for scenario in ["negative inventory", "duplicate ID", "missing column"]:
    bad = df.copy()
    if scenario == "negative inventory":
        bad.loc[0, "inventory_value_inr"] = -1
    elif scenario == "duplicate ID":
        bad.loc[1, "pharmacy_id"] = bad.loc[0, "pharmacy_id"]
    else:
        bad = bad.drop(columns=["workflow"])
    try:
        validate_clean_data(bad)
    except DataValidationError as error:
        print(f"Rejected {scenario}: {error}")
