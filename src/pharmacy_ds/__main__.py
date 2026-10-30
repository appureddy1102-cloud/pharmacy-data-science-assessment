"""Allow `python -m pharmacy_ds` from an installed editable repository."""

from pharmacy_ds.pipeline import run_pipeline

if __name__ == "__main__":
    run_pipeline()
