# Create the GitHub repository and upload all files

## Current status
**Repository location:** [appureddy1102-cloud/pharmacy-data-science-assessment](https://github.com/appureddy1102-cloud/pharmacy-data-science-assessment) — **private**. This location was returned by GitHub's authenticated repository-creation API, not guessed. Sign in as the owner or obtain collaborator access. The local Git exercise remains a disposable demonstration, not this repository's submission history. No credential is stored in the project. Revoke any token exposed in chat.

### Open, clone and share the existing repository

- Open https://github.com/appureddy1102-cloud/pharmacy-data-science-assessment while signed in to the owner account. A 404 while signed out does not mean a private repository is missing.
- To grant assessment access, open the repository's **Settings → Collaborators / Manage access**, invite the intended assessor, and have them accept the invitation.
- For future local changes, use your own browser login and clone the existing repository:

```bash
gh auth login --hostname github.com --git-protocol https --web
gh repo clone appureddy1102-cloud/pharmacy-data-science-assessment
cd pharmacy-data-science-assessment
git status
```

Review edits, create focused commits and push. The creation instructions later in this guide are for publishing **another copy**, not for recreating the existing repository.

### Optional continuous integration

The authorized credential permitted repository access but did not include workflow-installation permission. The complete CI configuration is therefore supplied at **docs/CI_WORKFLOW_TEMPLATE.yml**, not as an active .github/workflows file. If required, use GitHub's web editor to create `.github/workflows/tests.yml` with that template's content, commit it and review its actual Actions result. No broader token permissions were requested, and no cloud CI success is claimed.

## Publishing another copy

The steps below are retained for reproducibility and for uploading a separate copy under another unused repository name.

## 1. Secure your account first
If you shared a personal access token in chat, treat it as compromised.

1. On GitHub open your profile picture → **Settings → Developer settings → Personal access tokens → Tokens (classic)** (or Fine-grained tokens, as appropriate).
2. Locate the exposed token and delete/revoke it. Do not paste it into this project, another chat or a Git URL.
3. Review your account security log and repositories for unexpected activity. Replace any legitimate integrations that relied on the old credential through their secure configuration.
4. Use GitHub CLI's browser login or GitHub Desktop for the upload below; do not send a replacement token to the assistant.

Official guidance: [Managing personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) and [Keeping API credentials secure](https://docs.github.com/en/rest/authentication/keeping-your-api-credentials-secure).

## 2. Extract and review the project
- Extract `pharmacy-data-science-assessment.zip` on your computer.
- Open the extracted `pharmacy-data-science-assessment` folder. It should directly contain README.md, src/, exercises/, data/, notebooks/, reports/ and docs/.
- Do not merely upload the ZIP file as the repository's only content. Upload the extracted files and preserve their folder paths.
- Review `docs/SUBMISSION_CHECKLIST.md`, the Word report and `reports/test_results.txt`. Add your personal academic details if your assessor requires them.
- The standard dependency file is lowercase `requirements.txt`, which is conventional on GitHub.

## 3. Recommended: Git + GitHub CLI (browser authentication)
Install Git and GitHub CLI from their official sites if needed. Open Terminal, PowerShell or Git Bash **inside the extracted project folder**.

Authenticate using your own browser on your computer:

```bash
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
```

Follow the displayed browser/device-code prompts. Do not type a token into a shared command or store it in a repository file.

Configure your actual commit identity locally. Replace the explanatory text in quotes with your GitHub name and a verified email or GitHub-provided noreply email:

```bash
git init -b main
git config --local user.name "Your actual name"
git config --local user.email "Your verified or GitHub noreply email"
git add .
git diff --cached --stat
git status --short
git commit -m "Complete pharmacy data science fundamentals assessment"
```

Review the staged files before committing. Do not commit credentials, patient data, .venv/ or caches. The .gitignore already excludes common private and generated files.

Create and push the repository (private is safer for an assessment unless your assessor requires public):

```bash
gh repo create pharmacy-data-science-assessment --private --source=. --remote=origin --push
```

If you intentionally want a public portfolio and have permission, replace `--private` with `--public`. If that name already exists in your account, choose another unused repository name. Do not overwrite an existing repository without reviewing it.

**Retrieve the genuine final repository link after the push succeeds:**

```bash
gh repo view --json url --jq .url
gh repo view --web
```

The first command prints your real URL. Copy that URL into your assessment submission. It cannot be known from this local project alone, and a guessed URL is not proof of upload.

For subsequent edits:

```bash
git switch -c improve-documentation
# Edit and review the relevant files.
git add README.md docs/
git diff --cached
git commit -m "Clarify assessment reproduction steps"
git push -u origin improve-documentation
gh pr create --fill
```

If you are not using pull requests for this individual submission, you can commit reviewed changes on main and run `git push`. Do not force-push or replace a remote origin merely to silence an error.

## 4. Alternative: GitHub Desktop
1. Install and sign in to GitHub Desktop using its browser flow.
2. Choose **File → Add local repository**, select the extracted project folder, and if it is not yet a Git repository, follow the offered **create a repository here** action.
3. Confirm the repository root contains the existing README and project folders; avoid accidentally creating a second nested project folder.
4. Review changed files, enter an informative summary and commit to main.
5. Click **Publish repository**, choose the repository name and intended visibility, then publish.
6. Choose **View on GitHub** and copy the actual repository URL.

## 5. Alternative: browser upload
1. Sign in to GitHub and choose **New repository**.
2. Enter a name, description and intended visibility. For an existing project, do not initialize with another README, .gitignore or license.
3. Create the empty repository, choose **uploading an existing file** or **Add file → Upload files**, and drag the extracted folder's contents into the upload area.
4. Preserve src/, exercises/, scripts/, tests/, notebooks/, data/, docs/ and reports/ paths. Hidden files such as .gitignore may need special handling; Git/CLI is more reliable for them. The optional CI template is in docs/CI_WORKFLOW_TEMPLATE.yml.
5. Review the files and commit the upload. If the browser imposes a file-count limit, upload in smaller groups.
6. Check the repository home page and copy the address from your browser after confirming files are present.

## 6. Final verification on GitHub
- README renders; code, datasets, report and the executed notebook are visible.
- The notebook includes printed outputs and embedded figures.
- The optional CI template is present. If you choose to install it as an active Actions workflow, review its first actual run. Local tests passing does not guarantee cloud CI.
- For a private repository, grant the assessor appropriate access; a private URL alone does not grant access.
- Optionally create a `v1.0.0` release after review. Share the repository URL, the report and any required release link.

Official command-line reference: [Adding locally hosted code to GitHub](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github).
