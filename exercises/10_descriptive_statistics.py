"""Task 10: a hand-checkable example plus statistics on observed site waits."""

import numpy as np
from scipy import stats

from pharmacy_ds.cleaning import load_cleaned
from pharmacy_ds.config import PROJECT_ROOT

values = np.array([2, 4, 4, 4, 5, 5, 7, 9])
print(f"Toy mean={np.mean(values):.3f}; median={np.median(values):.3f}")
print(f"Toy mode={int(stats.mode(values, keepdims=False).mode)}")
print(f"Toy population variance={np.var(values, ddof=0):.3f}")
print(f"Toy sample variance={np.var(values, ddof=1):.3f}")
print(f"Toy sample SD={np.std(values, ddof=1):.3f}")
df = load_cleaned(PROJECT_ROOT / "data/processed/pharmacy_operations_clean.csv")
y = df["mean_wait_minutes"].dropna()
print(f"Observed site waits: n={len(y)}, mean={y.mean():.3f}, median={y.median():.3f}")
print(f"Sample variance={y.var(ddof=1):.3f}; sample SD={y.std(ddof=1):.3f}")
print(
    "Staff modes (descriptive; includes imputations):",
    df["staff_on_duty"].mode().tolist(),
)
