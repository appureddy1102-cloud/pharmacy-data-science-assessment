"""Generate README, findings and practical documentation from actual results."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def build_documentation():
    """Do not type sample results by hand: reuse captured execution evidence."""
    result = load("reports/statistical_results.json")
    audit = load("reports/cleaning_audit.json")
    exercises = load("reports/exercise_outputs.json")
    metadata = load("docs/exercises_metadata.json")
    environment = load("reports/execution_environment.json")
    repository_path = ROOT / "reports/github_repository.json"
    repository = (
        json.loads(repository_path.read_text(encoding="utf-8"))
        if repository_path.exists()
        else None
    )
    if repository:
        publishing_notice = (
            f"> **GitHub repository:** [{repository['full_name']}]({repository['html_url']}) — **private**. "
            "Sign in with the owner account or obtain collaborator access. "
            "The report includes the same repository location. No cloud CI run is claimed. "
            "See [the access and upload guide](docs/GITHUB_UPLOAD.md). "
            "Revoke any access token exposed in chat; no token is stored in these files."
        )
        github_steps = (
            "## GitHub access and future updates\n\n"
            f"Repository: **[{repository['full_name']}]({repository['html_url']})** (private). "
            "Invite your assessor through the repository's access settings if needed. "
            "Use browser-based authentication on your own computer for future changes:\n\n"
            "```bash\ngh auth login --hostname github.com --git-protocol https --web\n"
            f"gh repo clone {repository['full_name']}\ncd {repository['name']}\n"
            "git status\n```\n\n"
            "Review edits, commit focused changes and push using your approved local authentication. "
            "Do not create another repository with the same name just to update this one. "
            "[GITHUB_UPLOAD.md](docs/GITHUB_UPLOAD.md) covers access, updates and publishing another copy. "
            "The optional CI configuration is at `docs/CI_WORKFLOW_TEMPLATE.yml`; enable it through "
            "GitHub's web editor or an appropriately authorized connection if required. "
            "No active workflow or successful cloud CI execution is claimed."
        )
    else:
        publishing_notice = "> **Publishing status:** this is an upload-ready folder; no remote repository location has been recorded."
        github_steps = "## GitHub upload\n\nFollow [GITHUB_UPLOAD.md](docs/GITHUB_UPLOAD.md) to create and upload a new repository safely."
    tests = (ROOT / "reports/test_results.txt").read_text(encoding="utf-8").strip()
    match = re.search(r"(\d+) passed", tests)
    count = int(match.group(1)) if match else 0
    w, t, c, p = (
        result[k] for k in ["wait", "welch_test", "correlation", "probability"]
    )
    overview = (
        (ROOT / "reports/statistical_results.txt").read_text(encoding="utf-8").strip()
    )
    structure = """pharmacy-data-science-assessment/
├── README.md
├── requirements.txt              # tested, pinned dependencies
├── pyproject.toml                # editable Python package + tooling
├── .gitignore
├── docs/CI_WORKFLOW_TEMPLATE.yml # optional CI template; not an active workflow
├── src/pharmacy_ds/              # generation, cleaning, statistics, plots
├── exercises/                    # 16 runnable beginner practicals
├── scripts/                      # run, verify, notebook and report builders
├── tests/                        # schema, edge-case and numerical checks
├── notebooks/
│   └── 01_fundamentals_assessment.ipynb  # executed, embedded outputs
├── data/
│   ├── raw/pharmacy_operations_dirty.csv
│   ├── processed/pharmacy_operations_clean.csv
│   ├── processed/rejected_rows.csv
│   └── data_dictionary.csv
├── reports/
│   ├── Data_Science_Fundamentals_Assessment.docx
│   ├── figures/                  # seven PNG charts
│   ├── tables/                   # descriptive and workflow CSV tables
│   ├── cleaning_audit.json
│   ├── statistical_results.json and .txt
│   ├── exercise_outputs.json and .txt
│   ├── test_results.txt
│   └── execution / notebook / verification evidence
└── docs/                         # theory, dictionary, findings, upload guide"""
    readme = f"""# Data Science Fundamentals Assessment

## Pharmacy operations analytics | B.Pharm → Data Analytics

A complete beginner-level assessment portfolio covering Python, NumPy, Pandas, statistics, data types, cleaning, EDA, visualization, testing and Git. The real-world **context** is pharmacy operations; the **data are entirely synthetic**.

**Local verification:** {len(exercises)} practical exercises executed; **{count} tests passed**; seven EDA charts generated. The executed notebook, actual output logs and dependency versions are included. This is local evidence, **not a claim that GitHub Actions has run**.

> **Safety and honesty:** no patient data, clinical advice or measured business results are used. The generator deliberately includes a workflow effect. Statistics demonstrate methods, not real-world efficacy or an operational recommendation.
>
{publishing_notice}

## What this project demonstrates

- Python variables, types, lists, tuples, sets, dictionaries, conditionals, loops, functions and specific exception handling.
- NumPy arrays and vectorized operations; Pandas DataFrames, filtering, grouping and dtype management.
- Mean, median, mode, sample variance/SD, probability, normal distributions, covariance, correlation and Welch hypothesis testing.
- Numerical, categorical, nominal, ordinal, discrete, continuous, structured and unstructured data.
- Audited missing-value handling, exact deduplication, invalid-row quarantine, EDA and labeled plots.
- Clean modular code, documentation, data validation, tests, Git workflow and credential hygiene.

## Deliverables

| Deliverable | Location |
|---|---|
| Professional Word report | [reports/Data_Science_Fundamentals_Assessment.docx](reports/Data_Science_Fundamentals_Assessment.docx) |
| Executed notebook | [notebooks/01_fundamentals_assessment.ipynb](notebooks/01_fundamentals_assessment.ipynb) |
| Practical Python files | [exercises/](exercises/) |
| Exact sources and captured outputs | [docs/PRACTICAL_EXERCISES.md](docs/PRACTICAL_EXERCISES.md) |
| Statistical analysis | [docs/ANALYSIS_FINDINGS.md](docs/ANALYSIS_FINDINGS.md) |
| Sample CSVs and dictionary | [data/](data/) and [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md) |
| Seven EDA visualizations | [reports/figures/](reports/figures/) |
| Setup and reproducibility | [docs/RUN_GUIDE.md](docs/RUN_GUIDE.md) |
| GitHub creation/upload instructions | [docs/GITHUB_UPLOAD.md](docs/GITHUB_UPLOAD.md) |
| Assessment checklist | [docs/SUBMISSION_CHECKLIST.md](docs/SUBMISSION_CHECKLIST.md) |

## Quick start

Use Python 3.13 (tested: {environment["python"].split()[0]}) and Git. From the extracted repository root:

```bash
python -m venv .venv
# Windows PowerShell: .\\.venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps
python scripts/verify_submission.py
```

The full verification refreshes the synthetic sample, analysis, all exercise outputs, tests, executed notebook, documentation and Word report. It stops on failure. See [RUN_GUIDE.md](docs/RUN_GUIDE.md) for individual commands, platform-specific activation and troubleshooting. JupyterLab is an optional interface; headless notebook execution is included through nbclient/ipykernel.

To run only the existing-data analysis and tests:

```bash
python scripts/run_assessment.py
python -m pytest -q
```

## Dataset and cleaning policy

One record represents one **fictional independent pharmacy**, not one prescription or patient. Seed 2026 produces 120 sites, then adds five exact duplicate rows. The CSV has {audit["input_rows"]} raw rows. Cleaning removes {audit["exact_duplicates_removed"]} exact duplicates and quarantines {audit["critical_rows_rejected"]} records with invalid ID, date or workflow, leaving **{audit["output_rows"]} sites**.

- Raw data stay unchanged when the analysis runs; the sample generator intentionally recreates them.
- Invalid numeric values become missing and are counted in the audit.
- Designated non-outcome numeric columns receive flagged median imputation; count medians are rounded.
- **Missing wait outcomes are never imputed:** {audit["missing_wait_outcomes_retained"]} remain missing; {audit["observed_wait_outcomes"]} observed outcomes enter the primary comparison.
- Workload/wait correlation uses only **{c["complete_observed_n"]} complete observed pairs**, excluding imputed workload inputs.
- Stock-risk categories use arbitrary teaching cutoffs (Low >=95%, Medium >=90% and <95%, High <90%). Risk counts include {audit["imputed_counts"]["stock_availability_pct"]} stock imputations and are not validated healthcare quality indicators.
- Region labels are contextual only; Unknown is retained rather than guessed.

Full decisions: [cleaning_audit.json](reports/cleaning_audit.json), [THEORY.md](docs/THEORY.md) and [DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md).

## Actual executed results

```text
{overview}
```

**Interpretation:** the mean difference of {t["difference_minutes"]:.3f} minutes is **Standard minus Barcode-assisted**, with a 95% CI from {t["ci95_low"]:.3f} to {t["ci95_high"]:.3f} minutes. At prespecified alpha=0.05 the two-sided Welch procedure rejects equal means in this simulation. The generating formula already included a workflow effect, so this is a worked statistical example, not evidence to adopt a real pharmacy system. A pharmacy-level mean is not an individual waiting-time distribution.

The workload correlation of {c["pearson_r"]:.4f} is exploratory and does not establish causation. Median imputation can distort distributions; complete-case inference can be biased in real data. See [ANALYSIS_FINDINGS.md](docs/ANALYSIS_FINDINGS.md) for denominators, diagnostics and limitations.

## EDA examples

![Observed site mean waits by workflow](reports/figures/02_wait_by_workflow.png)

![Observed workload and mean wait](reports/figures/03_workload_scatter.png)

All seven charts are local files. They identify units, sample definitions and imputation policy; Q–Q diagnostics are separate for each workflow.

## Repository structure

```text
{structure}
```

## Quality and reproducibility evidence

```text
{tests}
```

Tests independently check schema, accounting of rows, raw-data preservation, invalid values, flags, outcome missingness, category order, CSV round trips and agreement of the Welch statistic/CI with SciPy. See [test_results.txt](reports/test_results.txt), [notebook_execution.json](reports/notebook_execution.json), [execution_environment.json](reports/execution_environment.json) and [verification_summary.json](reports/verification_summary.json).

Use `python -m ruff check .` for lint and `python -m ruff format .` for consistent formatting. Pinned **requirements.txt** is the conventional lowercase dependency filename. Package metadata permits Python 3.11+, but this submission's recorded verification covers Python 3.13 only. No successful cloud CI run or external review is asserted.

{github_steps}

## Academic and professional use

Review and understand every solution before submission. Add personal academic details only if required and follow your institution's rules on assistance and attribution. No student identity, real study data, execution results or remote publication has been invented. No open-source license has been selected; choose an appropriate license before offering the project as open-source.

## References

The report and [docs/REFERENCES.md](docs/REFERENCES.md) cite the Python, NumPy, pandas, SciPy, NIST, PEP 8 and GitHub documentation consulted. All assessment-specific numerical outputs are locally computed from the included synthetic files.
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8")
    (ROOT / "docs/REPOSITORY_STRUCTURE.txt").write_text(
        structure + "\n", encoding="utf-8"
    )
    practical = [
        "# Practical exercises — executed solutions\n",
        "These are the exact submitted Python sources and the captured outputs from a real local execution. Run setup and the pipeline first. Sources live in exercises/; reusable implementations live in src/pharmacy_ds/.\n",
    ]
    for name, entry in exercises.items():
        description = metadata[name]
        practical += [
            f"## {description['title']}\n",
            f"**Task:** {description['task']}\n",
            f"**Source:** `exercises/{name}`\n",
            f"```python\n{entry['source'].rstrip()}\n```\n",
            f"**Actual captured output:**\n\n```text\n{entry['stdout'].rstrip()}\n```\n",
            f"**Explanation:** {description['explanation']}\n",
        ]
    (ROOT / "docs/PRACTICAL_EXERCISES.md").write_text(
        "\n".join(practical), encoding="utf-8"
    )
    cleaning_rows = "\n".join(
        f"| {col} | {audit['imputed_counts'][col]} | {audit['imputation_values'][col]} |"
        for col in audit["imputed_counts"]
    )
    group_rows = "\n".join(
        f"| {name} | {g['n']} | {g['missing_outcomes']} | {g['mean']:.3f} | {g['sample_sd']:.3f} | {g['shapiro_p']:.4f} |"
        for name, g in result["workflow_summary"].items()
    )
    findings = f"""# 7. Data analysis results and interpretation

## 7.1 Row accounting and data quality

| Stage | Row count | Explanation |
|---|---|---|
| Raw CSV | {audit["input_rows"]} | 120 synthetic sites plus 5 exact duplicate records |
| After exact deduplication | {audit["rows_after_exact_deduplication"]} | Only identical records were removed |
| Critical rejected records | {audit["critical_rows_rejected"]} | One invalid ID, one invalid workflow, one invalid date |
| Valid cleaned sites | {audit["output_rows"]} | One row per accepted fictional pharmacy |
| Observed wait outcomes | {audit["observed_wait_outcomes"]} | Required for wait summaries and Welch test |
| Missing wait outcomes | {audit["missing_wait_outcomes_retained"]} | Five original missing values plus one invalid negative value; not imputed |
| Complete observed workload/wait pairs | {c["complete_observed_n"]} | Excludes imputed prescription/staff inputs and absent outcomes |

Three region entries become Unknown (two missing, one unrecognized). Invalid numeric conversion counts and source CSV row numbers are recorded in the audit/rejection files. No raw rows are silently rewritten. The raw-missingness chart counts empty cells, not invalid but non-null strings/numbers; these are distinct quality problems.

## 7.2 Predictor imputation audit

| Column | Imputed cells | Median fill used |
|---|---|---|
{cleaning_rows}

Counts are filled with rounded whole-number medians. The expiry column required no replacements; its recorded median is a reproducible potential fill value. Boolean flags preserve which entries were estimated. Mean waits are never filled. Stock-risk counts include four imputed stock values and therefore remain descriptive only.

## 7.3 Descriptive statistics and EDA

Among {result["observed_wait_n"]} observed site mean waits, the mean is **{w["mean"]:.3f} minutes** and the median is **{w["median"]:.3f} minutes**. Sample variance is **{w["sample_variance"]:.3f} minutes squared** and sample SD is **{w["sample_sd"]:.3f} minutes**. Minimum and maximum observed site means are {w["minimum"]:.2f} and {w["maximum"]:.2f} minutes; the first and third quartiles are {w["q1"]:.3f} and {w["q3"]:.3f} minutes.

The IQR-fence exercise flags four possible wait outliers in the pooled distribution; they are retained because an outlier flag is not evidence of a recording error. Inspect them and their workflow context instead of deleting them to change a p-value. The histogram and box plot show distributions of site summaries, not individual waits.

| Workflow | Observed n | Missing waits | Mean (min) | Sample SD (min) | Shapiro p |
|---|---|---|---|---|---|
{group_rows}

The descriptive stock-risk counts are Low={result["risk_counts"]["Low"]}, Medium={result["risk_counts"]["Medium"]} and High={result["risk_counts"]["High"]}. Categories are ordered Low < Medium < High and are generated from teaching-only cutoffs. No validated risk or quality claim is implied.

## 7.4 Probability, covariance and correlation

Of the {p["observed_n"]} sites with an observed mean wait, {p["success_count"]} have a mean below 10 minutes, giving an empirical probability of **{p["empirical_probability"]:.4f}**. This is a site-level fraction, not the chance that a randomly selected individual waits less than 10 minutes. Unknown waits are excluded from both numerator and denominator.

Using {c["complete_observed_n"]} complete observed workload/wait pairs, Pearson r is **{c["pearson_r"]:.4f}** and sample covariance is **{c["sample_covariance"]:.4f} (prescriptions per staff member) × minutes**. The positive association means higher workload tends to accompany higher site mean wait in this simulation. It is exploratory, scale-dependent for covariance, and not causal evidence. Workflow may contribute to the pooled relationship.

The separate assumed model X ~ N(10, 2²) gives P(X <= 12)={result["normal_example"]["p_le_12"]:.4f} and P(8 <= X <= 12)={result["normal_example"]["p_8_to_12"]:.4f}. These model values are not estimates of the observed dataset's normality.

## 7.5 Primary hypothesis test: Welch comparison

**H0:** the two workflow population mean site waits are equal. **H1:** they differ. The prespecified procedure is a two-sided Welch independent-samples t-test at alpha=0.05, comparing **Standard minus Barcode-assisted**. Outcomes are observed only. [R4]

| Test quantity | Executed value |
|---|---|
| Difference in means | {t["difference_minutes"]:.3f} minutes |
| Standard error of difference | {t["standard_error"]:.4f} minutes |
| Welch t statistic | {t["t_statistic"]:.4f} |
| Welch-Satterthwaite degrees of freedom | {t["degrees_of_freedom"]:.3f} |
| Two-sided p-value | {t["p_value"]:.9f} |
| 95% confidence interval | [{t["ci95_low"]:.3f}, {t["ci95_high"]:.3f}] minutes |
| Decision at alpha=0.05 | {t["decision"]} |

The interval does not include zero, consistent with the small p-value. In this simulated sample, Standard has a higher mean site wait. This demonstrates the mechanics of comparison, uncertainty and reporting; it does not show that barcode systems improve a real pharmacy.

## 7.6 Assumption checks and limitations

- Each generator record is a distinct fictional pharmacy; duplicates are removed before analysis. Real clustered or repeated-site data would need a design-aware method rather than pretending every row is independent.
- Q-Q plots are examined separately by workflow. Shapiro-Wilk p-values are reported as diagnostics, not proof of normality. Neither group diagnostic rejects normality at 0.05 in this run, but that alone does not establish the assumption. [R5]
- Welch accommodates unequal variances; it does not remove dependence, selection bias, severe anomalies or measurement error.
- Six absent/invalid outcomes are excluded, not replaced. Complete-case analysis can be biased in real observational data. Predictors with imputed values are excluded from the workload correlation, but risk counts intentionally include flagged stock imputations.
- The workflow difference was deliberately built into the outcome-generating formula. Results have no external validity for a real business or patient population and no clinical interpretation.
- One primary mean-comparison test is specified. Correlation is exploratory; normality checks are diagnostics. No broad screening of subgroup p-values or post-hoc causal claims is presented.
- No actual intervention recommendation follows from a fictional dataset. A real study would require an appropriate sampling design, validated measurement definitions, power planning, missingness review and domain oversight.
"""
    (ROOT / "docs/ANALYSIS_FINDINGS.md").write_text(findings, encoding="utf-8")
    print(
        f"README, findings, repository tree and {len(exercises)} documented practicals refreshed from executed evidence."
    )


if __name__ == "__main__":
    build_documentation()
