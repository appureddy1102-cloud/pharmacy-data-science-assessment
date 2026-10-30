"""Task 09: explore groups, category counts and potential (not deleted) outliers."""

from pharmacy_ds.cleaning import load_cleaned
from pharmacy_ds.config import PROJECT_ROOT

df = load_cleaned(PROJECT_ROOT / "data/processed/pharmacy_operations_clean.csv")
print("Observed site waits by workflow:")
table = df.groupby("workflow", observed=True)["mean_wait_minutes"].agg(
    ["count", "mean", "median", "std"]
)
print(table.to_string(float_format=lambda number: f"{number:.3f}"))
print("Derived risk counts (include stock imputations):")
print(df["stock_risk"].value_counts(sort=False).to_string())
wait = df["mean_wait_minutes"].dropna()
q1, q3 = wait.quantile([0.25, 0.75])
iqr = q3 - q1
flag = (wait < q1 - 1.5 * iqr) | (wait > q3 + 1.5 * iqr)
print(f"IQR-fence potential wait outliers: {int(flag.sum())}; retained for analysis")
