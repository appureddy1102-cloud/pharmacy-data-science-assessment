"""Fail-fast reproduction and verification of every submitted deliverable."""

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify():
    """Record actual return codes and write a final source/artifact manifest."""
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    steps = [
        ("lint", ["-m", "ruff", "check", "."], "lint_results.txt"),
        (
            "generate_sample",
            ["scripts/generate_sample_data.py"],
            "generation_execution.txt",
        ),
        (
            "pipeline_and_exercises",
            ["scripts/run_assessment.py"],
            "pipeline_execution.txt",
        ),
        ("tests", ["-m", "pytest", "-q"], "test_results.txt"),
        ("notebook", ["scripts/execute_notebook.py"], "notebook_execution.txt"),
        (
            "generated_notebook_lint",
            ["-m", "ruff", "check", "notebooks"],
            "notebook_lint_results.txt",
        ),
        (
            "documentation",
            ["scripts/build_documentation.py"],
            "documentation_build.txt",
        ),
        ("word_report", ["scripts/build_report.py"], "report_build.txt"),
    ]
    evidence = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "running",
        "steps": [],
    }
    for name, arguments, log_name in steps:
        print(f"Running: {name}", flush=True)
        completed = subprocess.run(
            [sys.executable, *arguments],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=300,
        )
        (reports / log_name).write_text(
            completed.stdout + completed.stderr, encoding="utf-8"
        )
        evidence["steps"].append(
            {
                "step": name,
                "return_code": completed.returncode,
                "log": "reports/" + log_name,
            }
        )
        if completed.returncode:
            evidence["status"] = "failed"
            evidence["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
            (reports / "verification_summary.json").write_text(
                json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
            )
            print(completed.stdout + completed.stderr, file=sys.stderr)
            raise SystemExit(completed.returncode)
    evidence["status"] = "passed"
    evidence["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    (reports / "verification_summary.json").write_text(
        json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
    )
    ignored = {
        ".git",
        ".venv",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        ".ipynb_checkpoints",
        "node_modules",
        "build",
        "dist",
    }
    lines = []
    manifest = reports / "submission_manifest.sha256"
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == manifest:
            continue
        parts = path.relative_to(ROOT).parts
        if any(p in ignored or p.endswith(".egg-info") for p in parts):
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(ROOT).as_posix()}")
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        f"All {len(steps)} verification steps passed. Manifest covers {len(lines)} files."
    )
    return evidence


if __name__ == "__main__":
    verify()
