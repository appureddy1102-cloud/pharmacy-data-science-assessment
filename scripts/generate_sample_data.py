"""Recreate the synthetic input file deterministically; overwrites sample CSV."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pharmacy_ds.generate import generate_sample_data  # noqa: E402

if __name__ == "__main__":
    df = generate_sample_data(ROOT / "data/raw/pharmacy_operations_dirty.csv")
    print(f"Generated {len(df)} raw rows using seed 2026 (120 sites + 5 duplicates).")
