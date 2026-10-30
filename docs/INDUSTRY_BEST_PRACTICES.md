# 8. Industry best practices

## 8.1 Readable, maintainable Python
Use descriptive snake_case names, four-space indentation, focused functions, explicit units in names and a consistent formatter. Separate data generation, cleaning, statistics and visualization into modules rather than placing every operation in one notebook cell. Keep configuration in one place and avoid magic thresholds with no explanation. Follow PEP 8 while prioritizing clarity. [R7]

Use vectorized column operations where they make intent clearer. Avoid hidden global state, mutable default arguments and broad exception swallowing. Type hints and docstrings communicate contracts; tests and runtime checks verify them. Specify ddof, comparison direction, category order and random seeds explicitly when they affect meaning.

## 8.2 Documentation and provenance
A professional README explains the problem, installation, data provenance, how to run the work, actual results, limitations and repository structure. A data dictionary defines units, ranges, missingness rules and category meanings. Comments explain why a choice was made, not merely restate each line. Maintain raw data separately from derived data, and log file hashes and package versions.

The report, notebook, CSVs and code must agree. This submission generates its practical output directly from the source files. The executed notebook embeds its chart outputs, so a reviewer does not need external image links. Only locally executed checks are presented as local evidence. A GitHub location is recorded only when returned by the authenticated API; no cloud CI result or third-party review is implied.

## 8.3 Validation, errors and tests
Validate required columns, types, valid categories, record uniqueness, nonfinite numbers, sensible ranges and consistency of derived variables. Distinguish an exact duplicate record from a contradictory record sharing the same ID. Preserve rejected rows and reasons for review. Avoid deleting unusual but plausible observations merely to obtain a more attractive p-value.

Raise clear, specific errors when a valid analysis cannot continue. Catch only expected input errors and give the user an actionable message. Do not hide failures behind fabricated zeros or empty charts. Use unit tests for edge cases and independent numerical checks; include a reproducible end-to-end run and a notebook execution check. Use explicit runtime checks rather than Python assert for production validation, because assert can be disabled; assertions remain appropriate in tests.

## 8.4 Statistical and visualization integrity
State the observational unit, analysis denominator, missing-value policy, hypotheses and alpha. Report effect estimates and confidence intervals, not just whether p is below 0.05. Do not equate statistical with practical or clinical significance. Avoid causal language for an exploratory correlation. If many formal comparisons are performed, prespecify and justify a multiplicity strategy rather than cherry-picking small p-values.

Use clear titles, axis labels, units and sample definitions. Do not use 3D effects or misleading axes. Distinguish observed values from imputations. A chart of site means cannot establish the distribution of individual patient waits. Diagnose distributions within relevant groups instead of treating a pooled mixture as one homogeneous population.

## 8.5 Git, GitHub and security
Git is a local version-control system; GitHub is a remote hosting and collaboration service. A repository contains files, commits and branches. The staging area selects changes for the next commit. Use `git status`, inspect staged differences, make focused commits and write informative commit messages. Use a feature branch and pull request for review before merging to main. Resolve conflicts thoughtfully rather than overwriting another person's work. [R8]

Use a .gitignore for virtual environments, caches, local configuration and credentials. Small synthetic sample data and assessment figures are tracked intentionally. Real patient records, account secrets, access tokens, passwords and private keys must never be committed. Use approved secure storage, least privilege and time-limited access. If a credential is exposed, revoke it and inspect account activity; deleting it from a document or chat does not make it secret again. [R9, R10]

The provided Git exercise makes a real local commit in a disposable directory using an explicitly fictional demonstration identity and a fixed date for repeatability. It does not create a GitHub repository. The optional GitHub Actions configuration is supplied at docs/CI_WORKFLOW_TEMPLATE.yml rather than as an active workflow, because the authorized credential did not grant workflow-installation permission. The owner can enable it using GitHub's web editor or an appropriately authorized connection. No cloud execution is claimed. Safe publishing instructions use a browser authentication flow rather than embedding a token in a command, URL or file.

## 8.6 Pharmacy-specific professional conduct
Use only approved data and access controls. De-identification and authorization requirements still apply when real health data are available. Apply institutional policies and applicable law; a generic portfolio is not a compliance certification. Validate operational definitions with qualified domain staff before applying an analysis to a pharmacy workflow.

This project contains no patient records or clinical recommendations. Synthetic examples teach methods but do not establish medicine quality, safety, efficacy, dosing or validated stock thresholds. Review and understand the work before assessment submission and follow your institution's rules about permitted assistance and attribution.
