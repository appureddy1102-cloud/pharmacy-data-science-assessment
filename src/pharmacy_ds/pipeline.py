"""Orchestrate real calculations and store submission evidence."""

import contextlib
import hashlib
import importlib.metadata
import io
import json
import os
import platform
import runpy
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from pharmacy_ds.cleaning import clean_data
from pharmacy_ds.config import NUMERIC_COLUMNS, PROJECT_ROOT
from pharmacy_ds.statistics import analyze, format_summary
from pharmacy_ds.visualization import create_figures


def save_json(path: Path, data: dict) -> None:
    """Write interoperable JSON; refuse NaN/Infinity rather than hiding an error."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def run_exercises(root: Path) -> dict:
    """Execute each exact exercise file and capture its actual printed output."""
    captured = {}
    for path in sorted((root / "exercises").glob("[0-9][0-9]_*.py")):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            runpy.run_path(str(path), run_name="__main__")
        captured[path.name] = {
            "source": path.read_text(encoding="utf-8"),
            "stdout": stream.getvalue(),
        }
    save_json(root / "reports" / "exercise_outputs.json", captured)
    plain = "\n".join(
        f"=== {name} ===\n{entry['stdout']}" for name, entry in captured.items()
    )
    (root / "reports" / "exercise_outputs.txt").write_text(plain, encoding="utf-8")
    return captured


def run_pipeline(root: Path = PROJECT_ROOT, include_exercises: bool = True) -> dict:
    """Read (never modify) raw data; write clean data, analysis, tables and charts."""
    root = Path(root).resolve()
    raw_path = root / "data/raw/pharmacy_operations_dirty.csv"
    if not raw_path.exists():
        raise FileNotFoundError("Run python scripts/generate_sample_data.py first.")
    raw = pd.read_csv(raw_path)
    cleaned, rejected, audit = clean_data(raw)
    processed = root / "data/processed"
    tables = root / "reports/tables"
    processed.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(processed / "pharmacy_operations_clean.csv", index=False)
    rejected.to_csv(processed / "rejected_rows.csv", index=False)
    save_json(root / "reports/cleaning_audit.json", audit)
    result = analyze(cleaned)
    save_json(root / "reports/statistical_results.json", result)
    text = format_summary(result)
    (root / "reports/statistical_results.txt").write_text(text, encoding="utf-8")
    cleaned[NUMERIC_COLUMNS + ["workload_per_staff"]].describe().T.to_csv(
        tables / "descriptive_statistics.csv"
    )
    pd.DataFrame(result["workflow_summary"]).T.to_csv(
        tables / "workflow_summary.csv", index_label="workflow"
    )
    pd.DataFrame({"raw_missing_cells": raw.isna().sum()}).to_csv(
        tables / "raw_missingness.csv", index_label="column"
    )
    figures = create_figures(raw, cleaned, root / "reports/figures")
    packages = [
        "numpy",
        "pandas",
        "scipy",
        "matplotlib",
        "seaborn",
        "python-docx",
        "nbformat",
        "nbclient",
        "ipykernel",
        "pytest",
        "ruff",
    ]
    environment = {
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "packages": {name: importlib.metadata.version(name) for name in packages},
        "raw_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        "clean_sha256": hashlib.sha256(
            (processed / "pharmacy_operations_clean.csv").read_bytes()
        ).hexdigest(),
        "seed": 2026,
        "figures_written": len(figures),
    }
    save_json(root / "reports/execution_environment.json", environment)
    # Exercises use the saved files so their outputs match the submitted CSVs.
    if include_exercises:
        prior_cwd = Path.cwd()
        try:
            os.chdir(root)
            run_exercises(root)
        finally:
            os.chdir(prior_cwd)
    print(text, end="")
    print(f"Figures saved: {len(figures)}")
    return result
