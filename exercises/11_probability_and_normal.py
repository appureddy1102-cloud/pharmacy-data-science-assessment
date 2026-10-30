"""Task 11: empirical, conditional and model-based probabilities."""

from scipy import stats

from pharmacy_ds.cleaning import load_cleaned
from pharmacy_ds.config import PROJECT_ROOT

print(f"3 damaged packs out of 20: P(damaged)={3 / 20:.4f}")
print(f"Two damaged, with replacement: {(3 / 20) ** 2:.4f}")
print(f"Two damaged, without replacement: {(3 / 20) * (2 / 19):.4f}")
df = load_cleaned(PROJECT_ROOT / "data/processed/pharmacy_operations_clean.csv")
observed = df.dropna(subset=["mean_wait_minutes"])
successes = int(observed["mean_wait_minutes"].lt(10).sum())
print(
    f"P(site mean wait < 10 | observed)={successes}/{len(observed)}={successes / len(observed):.4f}"
)
for workflow in ["Standard", "Barcode-assisted"]:
    group = observed.loc[observed["workflow"].eq(workflow), "mean_wait_minutes"]
    print(f"P(site mean wait < 10 | {workflow})={group.lt(10).mean():.4f}")
print("Hypothetical normal model: X ~ N(10, 2^2); not fitted to these data")
print(f"z at X=12: {(12 - 10) / 2:.1f}")
print(f"P(X <= 12)={stats.norm.cdf(12, loc=10, scale=2):.4f}")
print(f"P(8 <= X <= 12)={stats.norm.cdf(12, 10, 2) - stats.norm.cdf(8, 10, 2):.4f}")
