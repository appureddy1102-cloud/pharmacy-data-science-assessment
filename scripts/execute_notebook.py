"""Build and execute the notebook from the exact submitted exercise sources."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def execute_notebook():
    """Save an executed notebook only after all cells complete successfully."""
    metadata = json.loads(
        (ROOT / "docs/exercises_metadata.json").read_text(encoding="utf-8")
    )
    cells = [
        nbformat.v4.new_markdown_cell(
            "# Data Science Fundamentals Assessment\n"
            "## B.Pharm → Data Analytics | Synthetic pharmacy operations\n\n"
            "**Educational only:** 120 fictional independent sites, deliberately injected defects, "
            "no patient records. Each site has one summary observation. The generator includes a "
            "workflow effect; statistical results are not real-world evidence.\n\n"
            "Run cells from top to bottom. The submitted notebook includes actual executed outputs. "
            "CSV formats cannot preserve Pandas categories; `load_cleaned()` restores them. "
            "Setup reruns analysis against the supplied raw CSV without altering it."
        )
    ]
    cells.append(
        nbformat.v4.new_code_cell(
            "import sys\nfrom pathlib import Path\n\n"
            "ROOT = Path.cwd().resolve()\n"
            "if not (ROOT / 'src').is_dir():\n    ROOT = ROOT.parent\n"
            "if not (ROOT / 'src').is_dir():\n    raise RuntimeError('Start Jupyter in the repository root or notebooks folder.')\n"
            "sys.path.insert(0, str(ROOT / 'src'))\n"
            "from pharmacy_ds.pipeline import run_pipeline\n\n"
            "_ = run_pipeline(ROOT, include_exercises=False)"
        )
    )
    for path in sorted((ROOT / "exercises").glob("[0-9][0-9]_*.py")):
        entry = metadata[path.name]
        cells.append(
            nbformat.v4.new_markdown_cell(
                f"## {entry['title']}\n\n**Task:** {entry['task']}\n\n"
                f"**Why it matters:** {entry['explanation']}"
            )
        )
        cells.append(nbformat.v4.new_code_cell(path.read_text(encoding="utf-8")))
    cells.append(
        nbformat.v4.new_markdown_cell(
            "## EDA visual evidence\n\n"
            "Images below are embedded outputs, not remote resources. Wait plots use observed "
            "outcomes. The scatter excludes imputed workload inputs; risk counts include flagged "
            "stock imputations. Q–Q plots examine each workflow separately."
        )
    )
    for path in sorted((ROOT / "reports/figures").glob("*.png")):
        cells.append(
            nbformat.v4.new_code_cell(
                "from IPython.display import Image, display\n\n"
                f"display(Image(filename=str(ROOT / 'reports/figures/{path.name}')))"
            )
        )
    cells.append(
        nbformat.v4.new_markdown_cell(
            "## Interpretation and integrity\n\n"
            "The Welch test compares pharmacy-level mean waits, **not individual waiting times**. "
            "Missing outcomes are not imputed; correlation uses complete observed inputs. "
            "Inspect `reports/statistical_results.json`, `reports/cleaning_audit.json` and "
            "`reports/test_results.txt` for reproducible evidence. No GitHub publishing occurs "
            "in this notebook. References and limitations are documented in `docs/`."
        )
    )
    notebook = nbformat.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": sys.version.split()[0]},
        },
    )
    client = NotebookClient(
        notebook,
        timeout=180,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
    )
    client.execute()
    nbformat.validate(notebook)
    destination = ROOT / "notebooks/01_fundamentals_assessment.ipynb"
    nbformat.write(notebook, destination)
    code = [cell for cell in notebook.cells if cell.cell_type == "code"]
    evidence = {
        "status": "passed",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "code_cells": len(code),
        "executed_cells": sum(c.execution_count is not None for c in code),
        "error_outputs": sum(o.output_type == "error" for c in code for o in c.outputs),
        "embedded_images": sum(
            "image/png" in o.get("data", {}) for c in code for o in c.outputs
        ),
    }
    (ROOT / "reports/notebook_execution.json").write_text(
        json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(evidence, indent=2))
    return evidence


if __name__ == "__main__":
    execute_notebook()
