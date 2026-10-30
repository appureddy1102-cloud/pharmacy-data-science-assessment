"""Demonstrate actual local Git commands in an automatically removed directory."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def run_git_demo() -> str:
    """Return captured Git output; no remote, credentials or network are used."""
    if shutil.which("git") is None:
        return "Git is not installed. Install Git to run this optional local demonstration.\n"
    env = os.environ.copy()
    # Fixed demonstration identity/date give repeatable local commit output.
    env.update(
        {
            "GIT_AUTHOR_NAME": "Assessment demonstration",
            "GIT_AUTHOR_EMAIL": "assessment@example.invalid",
            "GIT_COMMITTER_NAME": "Assessment demonstration",
            "GIT_COMMITTER_EMAIL": "assessment@example.invalid",
            "GIT_AUTHOR_DATE": "2026-10-30T12:00:00+05:30",
            "GIT_COMMITTER_DATE": "2026-10-30T12:00:00+05:30",
        }
    )
    output = []
    with tempfile.TemporaryDirectory(prefix="pharmacy-git-demo-") as directory:
        root = Path(directory)
        (root / "README.md").write_text(
            "# Synthetic pharmacy assessment\n", encoding="utf-8"
        )
        commands = [
            ["git", "init", "--quiet", "-b", "main"],
            ["git", "add", "README.md"],
            ["git", "diff", "--cached", "--stat"],
            [
                "git",
                "-c",
                "commit.gpgsign=false",
                "commit",
                "--quiet",
                "-m",
                "Add assessment README",
            ],
            ["git", "log", "-1", "--oneline"],
            ["git", "status", "--short"],
        ]
        for command in commands:
            result = subprocess.run(
                command,
                cwd=root,
                env=env,
                capture_output=True,
                text=True,
                check=True,
                timeout=20,
            )
            output.append("$ " + " ".join(command))
            if result.stdout.strip():
                output.append(result.stdout.strip())
        output.append(
            "Clean working tree; local demonstration only. No GitHub repository was created."
        )
    return "\n".join(output) + "\n"
