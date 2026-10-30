"""Run all Python practicals and produce real analysis outputs."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pharmacy_ds.pipeline import run_pipeline  # noqa: E402

if __name__ == "__main__":
    run_pipeline(ROOT)
