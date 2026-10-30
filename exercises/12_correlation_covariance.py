"""Task 12: observed-only sample covariance and Pearson correlation."""

from pharmacy_ds.cleaning import load_cleaned
from pharmacy_ds.config import PROJECT_ROOT
from pharmacy_ds.statistics import correlation_sample

df = load_cleaned(PROJECT_ROOT / "data/processed/pharmacy_operations_clean.csv")
observed = correlation_sample(df)
x = observed["workload_per_staff"]
y = observed["mean_wait_minutes"]
print(f"Complete observed workload/wait pairs: {len(observed)}")
print(f"Sample covariance: {x.cov(y, ddof=1):.4f}")
print("Covariance units: (prescriptions per staff member) * minutes")
print(f"Pearson correlation r: {x.corr(y):.4f}")
print("Correlation does not establish causation; workflow is a possible confounder.")
