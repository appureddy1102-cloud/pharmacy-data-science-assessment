"""Task 14: regenerate seven labeled chart files using Matplotlib and Seaborn."""

import pandas as pd

from pharmacy_ds.cleaning import load_cleaned
from pharmacy_ds.config import PROJECT_ROOT
from pharmacy_ds.visualization import create_figures

raw = pd.read_csv(PROJECT_ROOT / "data/raw/pharmacy_operations_dirty.csv")
df = load_cleaned(PROJECT_ROOT / "data/processed/pharmacy_operations_clean.csv")
paths = create_figures(raw, df, PROJECT_ROOT / "reports/figures")
print(f"Saved {len(paths)} figures:")
for path in paths:
    print(" ", path.relative_to(PROJECT_ROOT).as_posix())
