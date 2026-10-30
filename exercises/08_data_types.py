"""Task 08: analytical data types versus Python/Pandas storage types."""

from pharmacy_ds.cleaning import load_cleaned
from pharmacy_ds.config import PROJECT_ROOT

df = load_cleaned(PROJECT_ROOT / "data/processed/pharmacy_operations_clean.csv")
for column in [
    "pharmacy_id",
    "report_date",
    "workflow",
    "stock_risk",
    "daily_prescriptions",
    "mean_wait_minutes",
    "notes",
]:
    print(f"{column}: {df[column].dtype}")
print("Risk order:", df["stock_risk"].cat.categories.tolist())
print("Risk is ordered:", df["stock_risk"].cat.ordered)
print("CSV = structured table; notes content = unstructured text.")
print("An ID is nominal even when it contains digits.")
