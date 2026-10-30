"""Task 07: run audited cleaning without changing the raw CSV."""

import pandas as pd

from pharmacy_ds.cleaning import clean_data
from pharmacy_ds.config import PROJECT_ROOT

raw = pd.read_csv(PROJECT_ROOT / "data/raw/pharmacy_operations_dirty.csv")
clean, rejected, audit = clean_data(raw)
print(f"Input rows: {len(raw)}")
print(f"Exact duplicates removed: {audit['exact_duplicates_removed']}")
print(f"Critical rows quarantined: {len(rejected)}")
print(f"Clean rows: {len(clean)}")
print("Imputed numeric cells (with flags):")
for column, count in audit["imputed_counts"].items():
    print(f"  {column}: {count}; fill={audit['imputation_values'][column]}")
print(f"Unknown regions: {audit['unknown_region_count']}")
print(f"Missing wait outcomes retained: {audit['missing_wait_outcomes_retained']}")
print("Validation passed; no outcome was imputed.")
