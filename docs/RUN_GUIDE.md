# Reproduce the assessment

## Environment
The supplied results were executed with CPython 3.13.16 and the versions in requirements.txt. Python 3.13 is recommended. The package metadata permits Python 3.11+, but only the recorded Python environment has been verified for this submission. Use a fresh virtual environment; Internet access is needed to install dependencies, not to analyze the supplied data.

From the extracted repository root:

```bash
python -m venv .venv
```

Activate it on **Windows PowerShell**:

```powershell
.\.venv\Scripts\Activate.ps1
```

If your organization blocks PowerShell activation, use Command Prompt with `.venv\Scripts\activate.bat` or invoke `.venv\Scripts\python.exe` directly; do not weaken an organization security policy.

Activate it on **macOS / Linux**:

```bash
source .venv/bin/activate
```

Install the tested dependencies and the local package:

```bash
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps
```

## One-command full verification

```bash
python scripts/verify_submission.py
```

This checks lint, recreates the synthetic CSV, executes analysis and all 16 exercises, runs tests, executes the notebook, refreshes documentation and regenerates the Word report. Any failed step stops the process. Outputs under data/processed/, reports/, notebooks/ and generated docs are overwritten; the supplied sample generator intentionally replaces the synthetic raw CSV. Do not point it at real data.

## Individual steps

```bash
python scripts/generate_sample_data.py
python scripts/run_assessment.py
python -m pytest -q
python scripts/execute_notebook.py
python scripts/build_documentation.py
python scripts/build_report.py
python -m ruff check .
```

`run_assessment.py` reads the existing raw CSV without modifying it. It writes cleaned/rejected CSVs, an audit, statistical results, summary tables, seven PNGs, an environment record and actual exercise output logs. It requires the full supplied schema; it is not a generic cleaner for arbitrary health datasets.

Run a single exercise after setup and pipeline execution:

```bash
python exercises/13_hypothesis_testing.py
```

## Notebook use
The executed notebook is `notebooks/01_fundamentals_assessment.ipynb`. It can be reviewed as submitted without running it. To edit interactively, optionally install JupyterLab (`python -m pip install jupyterlab`) or use VS Code with Python/Jupyter extensions, select the same virtual environment and run cells top to bottom. JupyterLab is an optional interface, not required for headless execution through nbclient.

## Files that demonstrate actual execution
- reports/pipeline_execution.txt — captured pipeline output.
- reports/exercise_outputs.json and .txt — exact exercise sources and captured outputs.
- reports/test_results.txt — the actual pytest run, not a hand-written sample.
- reports/lint_results.txt — actual Ruff check output.
- reports/notebook_execution.json — executed cell and embedded-image counts.
- reports/execution_environment.json — actual execution timestamp, versions and SHA-256 data hashes.
- reports/verification_summary.json — full-run step status and completion time.

Statistical results and charts are deterministic for the same data and dependency versions. Execution timestamps and elapsed test times legitimately change between runs. Cross-platform floating-point differences may affect last decimal places. All quoted rounded results should agree to the displayed precision.

## Common issues
- **ModuleNotFoundError:** activate the intended environment, install requirements, and run `python -m pip install -e . --no-deps` from the repository root.
- **FileNotFoundError for the raw CSV:** run the sample generator first.
- **Kernel missing:** install requirements into the environment running the execution script; ipykernel is included.
- **Git not installed:** the optional local Git exercise prints a clear installation message. Install Git and rerun it to reproduce the supplied Git output.
- **Validation error:** inspect the raw schema and reports/cleaning_audit.json. Do not suppress validation simply to produce a result.
- **No internet on first install:** install dependencies through an approved local package mirror or wheelhouse. The analysis itself uses only local synthetic files.
