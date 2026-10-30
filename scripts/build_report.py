"""Build a polished .docx from documented theory and real execution evidence."""

import csv
import json
import re
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
NAVY = "16324F"
TEAL = "007F87"
GRAY = "526171"
PALE = "F0F5F8"
LIGHT_TEAL = "E8F4F3"


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def repository_notice(fallback):
    """Use an API-confirmed repository location without inventing a URL."""
    path = ROOT / "reports/github_repository.json"
    if not path.exists():
        return fallback
    repository = json.loads(path.read_text(encoding="utf-8"))
    visibility = "private" if repository.get("private") else "public"
    return (
        f"**GitHub repository ({visibility}):** {repository['html_url']}. "
        "Private repositories require owner sign-in or collaborator access. "
        "No access token is stored in the project; revoke any credential exposed in chat."
    )


def shade(element, fill):
    properties = (
        element.get_or_add_tcPr()
        if element.tag == qn("w:tc")
        else element.get_or_add_pPr()
    )
    previous = properties.find(qn("w:shd"))
    if previous is not None:
        properties.remove(previous)
    node = OxmlElement("w:shd")
    node.set(qn("w:fill"), fill)
    properties.append(node)


def inline(paragraph, text):
    """Render simple bold and inline-code markers, keeping all text editable."""
    for chunk in re.split(r"(\*\*.*?\*\*|`[^`]*`)", text):
        if not chunk:
            continue
        if chunk.startswith("**") and chunk.endswith("**"):
            run = paragraph.add_run(chunk[2:-2])
            run.bold = True
        elif chunk.startswith("`") and chunk.endswith("`"):
            run = paragraph.add_run(chunk[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor.from_string(NAVY)
        else:
            for piece in re.split(r"(https?://[^\s]+)", chunk):
                if piece.startswith(("https://", "http://")):
                    url = piece.rstrip(".,;")
                    relationship = paragraph.part.relate_to(
                        url, RT.HYPERLINK, is_external=True
                    )
                    hyperlink = OxmlElement("w:hyperlink")
                    hyperlink.set(qn("r:id"), relationship)
                    run = OxmlElement("w:r")
                    properties = OxmlElement("w:rPr")
                    color = OxmlElement("w:color")
                    color.set(qn("w:val"), TEAL)
                    properties.append(color)
                    underline = OxmlElement("w:u")
                    underline.set(qn("w:val"), "single")
                    properties.append(underline)
                    run.append(properties)
                    text = OxmlElement("w:t")
                    text.text = url
                    run.append(text)
                    hyperlink.append(run)
                    paragraph._p.append(hyperlink)
                    if piece[len(url) :]:
                        paragraph.add_run(piece[len(url) :])
                else:
                    paragraph.add_run(piece)
    return paragraph


def body(document, text, style=None):
    return inline(document.add_paragraph(style=style), text)


def table(document, headers, rows, widths=None):
    tab = document.add_table(rows=1, cols=len(headers))
    tab.alignment = WD_TABLE_ALIGNMENT.CENTER
    tab.autofit = False
    if widths:
        for column, width in zip(tab.columns, widths, strict=True):
            column.width = Inches(width)
    for i, title in enumerate(headers):
        cell = tab.rows[0].cells[i]
        if widths:
            cell.width = Inches(widths[i])
        shade(cell._tc, NAVY)
        paragraph = cell.paragraphs[0]
        paragraph.paragraph_format.space_after = Pt(4)
        paragraph.paragraph_format.space_before = Pt(4)
        run = paragraph.add_run(str(title))
        run.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)
        run.font.size = Pt(9)
    repeat = OxmlElement("w:tblHeader")
    tab.rows[0]._tr.get_or_add_trPr().append(repeat)
    for index, values in enumerate(rows):
        cells = tab.add_row().cells
        cant_split = OxmlElement("w:cantSplit")
        tab.rows[-1]._tr.get_or_add_trPr().append(cant_split)
        for col, value in enumerate(values):
            if widths:
                cells[col].width = Inches(widths[col])
            if index % 2 == 0:
                shade(cells[col]._tc, PALE)
            paragraph = cells[col].paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(4)
            paragraph.paragraph_format.space_before = Pt(4)
            paragraph.paragraph_format.line_spacing = 1.05
            inline(paragraph, str(value))
            for run in paragraph.runs:
                run.font.size = Pt(8.7)
    document.add_paragraph().paragraph_format.space_after = Pt(1)
    return tab


def code(document, text, output=False):
    """Keep Python and actual stdout monospaced and fully editable."""
    paragraph = document.add_paragraph(style="Output Block" if output else "Code Block")
    # The source text is unchanged, except for removing a trailing blank line.
    paragraph.add_run(text.rstrip())
    shade(paragraph._p, "F1F6F4" if output else "F3F5F7")
    paragraph.paragraph_format.keep_together = False
    return paragraph


def markdown(document, text, chapter_breaks=True):
    """Small deterministic renderer for this repository's controlled Markdown."""
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith("```"):
            block = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                block.append(lines[index])
                index += 1
            code(document, "\n".join(block))
            index += 1
            continue
        if line.startswith("|"):
            block = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                values = [v.strip() for v in lines[index].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", v) for v in values):
                    block.append(values)
                index += 1
            table(document, block[0], block[1:])
            continue
        if line.startswith("# "):
            if chapter_breaks:
                document.add_page_break()
            document.add_heading(line[2:], level=1)
        elif line.startswith("## "):
            document.add_heading(line[3:], level=2)
        elif line.startswith("### "):
            document.add_heading(line[4:], level=3)
        elif line.startswith("- "):
            body(document, line[2:], "List Bullet")
        elif re.match(r"\d+\. ", line):
            body(document, re.sub(r"^\d+\. ", "", line), "List Number")
        else:
            paragraph_lines = [line]
            while index + 1 < len(lines):
                following = lines[index + 1].strip()
                if (
                    not following
                    or following.startswith(("#", "|", "- ", "```"))
                    or re.match(r"\d+\. ", following)
                ):
                    break
                index += 1
                paragraph_lines.append(following)
            body(document, " ".join(paragraph_lines))
        index += 1


def configure(document):
    section = document.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Inches(0.68)
    section.bottom_margin = Inches(0.66)
    section.left_margin = Inches(0.72)
    section.right_margin = Inches(0.72)
    section.header_distance = Inches(0.28)
    section.footer_distance = Inches(0.28)
    section.different_first_page_header_footer = True
    normal = document.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor.from_string("253645")
    normal.paragraph_format.line_spacing = 1.12
    normal.paragraph_format.space_after = Pt(6)
    for name, size, color in [
        ("Title", 31, NAVY),
        ("Subtitle", 14, GRAY),
        ("Heading 1", 17, NAVY),
        ("Heading 2", 12.5, TEAL),
        ("Heading 3", 11, NAVY),
    ]:
        style = document.styles[name]
        style.font.name = "Calibri"
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor.from_string(color)
        style.font.bold = name != "Subtitle"
        style.paragraph_format.space_before = Pt(
            11 if name.startswith("Heading") else 4
        )
        style.paragraph_format.space_after = Pt(7)
    for name, fill in [("Code Block", "F3F5F7"), ("Output Block", "F1F6F4")]:
        style = document.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        style.font.name = "Consolas"
        style.font.size = Pt(8.1)
        style.font.color.rgb = RGBColor.from_string(
            "243B4D" if name == "Code Block" else "245747"
        )
        style.paragraph_format.space_before = Pt(3)
        style.paragraph_format.space_after = Pt(7)
        style.paragraph_format.left_indent = Inches(0.08)
        style.paragraph_format.right_indent = Inches(0.06)
        style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        style.paragraph_format.line_spacing = Pt(10)
    for name in ["List Bullet", "List Number"]:
        document.styles[name].paragraph_format.space_after = Pt(4)
    document.styles["Caption"].font.name = "Calibri"
    document.styles["Caption"].font.size = Pt(8.5)
    document.styles["Caption"].font.color.rgb = RGBColor.from_string(GRAY)
    document.styles["Caption"].paragraph_format.space_after = Pt(7)
    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = header.add_run("ASSESSMENT PORTFOLIO  /  PHARMACY DATA ANALYTICS")
    run.font.name = "Calibri"
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor.from_string(GRAY)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = footer.add_run("Synthetic educational data • not clinical evidence    |    ")
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor.from_string(GRAY)
    for tag, content in [("begin", None), (None, " PAGE "), ("separate", None)]:
        run = footer.add_run()
        if tag:
            field = OxmlElement("w:fldChar")
            field.set(qn("w:fldCharType"), tag)
        else:
            field = OxmlElement("w:instrText")
            field.set(qn("xml:space"), "preserve")
            field.text = content
        run._r.append(field)
    footer.add_run("1")
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    footer.add_run()._r.append(end)
    settings = document.settings.element
    update = OxmlElement("w:updateFields")
    update.set(qn("w:val"), "true")
    settings.append(update)
    language = OxmlElement("w:themeFontLang")
    language.set(qn("w:val"), "en-IN")
    settings.append(language)
    document.core_properties.title = "Data Science Fundamentals Assessment"
    document.core_properties.subject = (
        "Python, statistics, data types and synthetic pharmacy operations"
    )
    document.core_properties.author = "Assessment learning portfolio"
    document.core_properties.keywords = (
        "B.Pharm, data analytics, Python, Pandas, statistics, synthetic data"
    )
    document.core_properties.comments = "Generated from executed local synthetic-data evidence. An API-confirmed repository location is included when configured. No patient data or cloud CI results are claimed."


def cover(document, test_count, exercise_count):
    p = document.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    run = p.add_run("FOUNDATIONS  /  PHARMACY  /  ANALYTICS")
    run.bold = True
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor.from_string(TEAL)
    document.add_paragraph().paragraph_format.space_after = Pt(23)
    title = document.add_paragraph(style="Title")
    title.add_run("Data Science\nFundamentals\nAssessment")
    p = document.add_paragraph(style="Subtitle")
    p.add_run(
        "A practical, reproducible portfolio for a B.Pharm learner\nentering Data Analytics and a beginner internship"
    )
    p.paragraph_format.space_after = Pt(20)
    tab = document.add_table(rows=1, cols=1)
    cell = tab.cell(0, 0)
    shade(cell._tc, NAVY)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(13)
    p.paragraph_format.space_after = Pt(13)
    r = p.add_run("  SYNTHETIC PHARMACY OPERATIONS\n")
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)
    r = p.add_run(
        "  From raw data to validated analysis, visual evidence and clear reporting"
    )
    r.font.size = Pt(10.5)
    r.font.color.rgb = RGBColor.from_string("D9EAF0")
    document.add_paragraph().paragraph_format.space_after = Pt(11)
    table(
        document,
        ["PRACTICAL WORK", "QUALITY CHECKS", "VISUAL EVIDENCE"],
        [
            [
                f"{exercise_count} executed exercises",
                f"{test_count} tests passed locally",
                "7 labeled EDA charts",
            ]
        ],
    )
    body(document, "**Assessment level:** Beginner  |  **Domain:** Pharmacy operations")
    body(
        document,
        "**Report date:** 30 October 2026  |  **Format:** Academic assessment + technical portfolio",
    )
    p = body(
        document,
        "**Data integrity statement:** All datasets are generated for education. No patient records, clinical findings or real pharmacy performance results are presented. Every quoted execution output is captured from working Python code.",
    )
    shade(p._p, LIGHT_TEAL)
    body(
        document,
        repository_notice(
            "**Publication status:** Repository files are ready for GitHub upload; no repository location is configured."
        ),
    )


def chart_page(document, items, heading):
    document.add_page_break()
    document.add_heading(heading, level=2)
    for filename, caption in items:
        p = document.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        p.add_run().add_picture(
            str(ROOT / "reports/figures" / filename), width=Inches(6.53)
        )
        p = document.add_paragraph(caption, style="Caption")
        p.paragraph_format.keep_with_next = False


def build_report():
    result = load("reports/statistical_results.json")
    audit = load("reports/cleaning_audit.json")
    exercises = load("reports/exercise_outputs.json")
    metadata = load("docs/exercises_metadata.json")
    environment = load("reports/execution_environment.json")
    notebook = load("reports/notebook_execution.json")
    tests = (ROOT / "reports/test_results.txt").read_text(encoding="utf-8").strip()
    test_count = int(re.search(r"(\d+) passed", tests).group(1))
    document = Document()
    configure(document)
    cover(document, test_count, len(exercises))
    document.add_page_break()
    document.add_heading("Reader guide and contents", level=1)
    body(
        document,
        "This report combines beginner-friendly theory with reproducible practical evidence. The companion repository contains the original Python files, executed notebook, sample CSVs, generated charts, tests and upload documentation. File names identify exactly where a reviewer can reproduce each result.",
    )
    table(
        document,
        ["Section", "What to look for"],
        [
            [
                "1. Introduction and objectives",
                "Scope, pharmacy context and success criteria",
            ],
            ["2. Python fundamentals", "Core language concepts, NumPy and Pandas"],
            [
                "3. Statistical foundations",
                "Worked definitions, probability, models and inference",
            ],
            ["4. Understanding data types", "Measurement types and data organization"],
            [
                "5. Dataset and cleaning methodology",
                "Provenance, validation and missing-data decisions",
            ],
            [
                "6. Practical exercises",
                "16 exact Python sources, captured outputs and explanations",
            ],
            [
                "7. Analysis results and visual evidence",
                "Row audit, estimates, test, diagnostics and seven figures",
            ],
            [
                "8. Industry best practices",
                "Code quality, documentation, validation, Git and privacy",
            ],
            ["9. Conclusion", "Learning outcomes, limits and next steps"],
            ["10. References", "Authoritative sources and documentation"],
            [
                "Appendices A–C",
                "Run/upload instructions, dictionary, verification and file index",
            ],
        ],
        [2.4, 4.35],
    )
    body(
        document,
        "**Navigation:** use Word's Navigation Pane to jump between headings. This section guide intentionally avoids page numbers that may change across Word installations.",
    )
    body(
        document,
        "**How to interpret evidence:** a code block is the submitted executable source; a green-tinted output block is actual captured stdout. All paths are relative to the repository root. The report's date is an assessment date; precise execution times and package versions are stored in reports/execution_environment.json.",
    )
    body(
        document,
        "**Submission identity:** no student name, roll number or institution was supplied or invented. Add these to the cover only if required by your assessor; review the work and follow institutional attribution rules.",
    )
    markdown(document, (ROOT / "docs/THEORY.md").read_text(encoding="utf-8"))
    document.add_page_break()
    document.add_heading("6. Practical exercises: executed solutions", level=1)
    body(
        document,
        "The following 16 tasks were run successfully. Each includes a task statement, complete short Python source, actual captured output and an explanation. Source files import the companion package where full production-style implementation is needed. Run setup and the pipeline before executing an individual file.",
    )
    code(
        document,
        "python -m pip install -r requirements.txt\npython -m pip install -e . --no-deps\npython scripts/run_assessment.py\npython exercises/13_hypothesis_testing.py",
    )
    table(
        document,
        ["Tasks", "Skills demonstrated"],
        [
            ["01–04", "Variables, collections, control flow, functions and exceptions"],
            ["05–06", "NumPy arrays and Pandas tables"],
            ["07–09", "Cleaning, validation, data types and EDA"],
            [
                "10–13",
                "Descriptive statistics, probability, correlation and Welch inference",
            ],
            [
                "14–16",
                "Visualization, intentional validation failures and actual local Git history",
            ],
        ],
        [1.0, 5.75],
    )
    body(
        document,
        "**Verification principle:** exercise_outputs.json stores the source text and captured output together, reducing the risk of presenting output from a different code version. The report builder reads that record instead of typing numerical examples by hand.",
    )
    for index, (name, entry) in enumerate(exercises.items(), 1):
        document.add_page_break()
        label = metadata[name]["title"].split(" · ", 1)[-1]
        document.add_heading(f"6.{index:02d} {label}", level=2)
        body(document, f"**Task:** {metadata[name]['task']}")
        p = body(document, f"**Source file:** exercises/{name}")
        p.paragraph_format.space_after = Pt(3)
        body(document, "**Working Python code**")
        code(document, entry["source"])
        body(document, "**Actual captured output**")
        code(document, entry["stdout"], output=True)
        body(document, f"**Explanation:** {metadata[name]['explanation']}")
    markdown(document, (ROOT / "docs/ANALYSIS_FINDINGS.md").read_text(encoding="utf-8"))
    chart_page(
        document,
        [
            (
                "01_wait_histogram.png",
                "Figure 1. Histogram of 111 observed pharmacy-level mean waits. The dashed line is the sample mean. The unit is a pharmacy, not an individual patient.",
            ),
            (
                "02_wait_by_workflow.png",
                "Figure 2. Workflow box plots with observed site means. Standard has a higher sample mean; the Barcode-assisted group has greater observed spread. No outcome is imputed.",
            ),
        ],
        "7.7 Visual evidence — distributions and workflow comparison",
    )
    chart_page(
        document,
        [
            (
                "03_workload_scatter.png",
                "Figure 3. Workload versus observed site mean wait for 101 complete observed pairs. Imputed prescription/staff inputs are excluded. Colors identify workflow; association is not causation.",
            ),
            (
                "04_stock_risk_counts.png",
                "Figure 4. Ordered stock-risk counts: 36 Low, 74 Medium and 7 High. Four stock values are imputed. Cutoffs are teaching examples, not validated healthcare quality thresholds.",
            ),
        ],
        "7.8 Visual evidence — relationships and ordered categories",
    )
    chart_page(
        document,
        [
            (
                "05_raw_missingness.png",
                "Figure 5. Missing cells in the raw 125-row CSV. Invalid but non-null values, such as a negative wait or an unrecognized workflow, are separately counted in the cleaning audit.",
            ),
            (
                "06_qq_standard.png",
                "Figure 6. Standard workflow normal Q–Q diagnostic, n=55. Approximate alignment is a shape diagnostic, not proof of normality or independence.",
            ),
        ],
        "7.9 Visual evidence — quality and within-group diagnostics",
    )
    chart_page(
        document,
        [
            (
                "07_qq_barcode.png",
                "Figure 7. Barcode-assisted workflow normal Q–Q diagnostic, n=56. Examine tail departures and context alongside the reported Shapiro–Wilk diagnostic.",
            ),
        ],
        "7.10 Visual evidence — second workflow diagnostic",
    )
    body(
        document,
        "**Reading Q–Q plots:** points close to the reference line are consistent with an approximately normal shape. Departures, especially at the tails, require context. The reference line is fitted for visual comparison; it is not a regression model explaining pharmacy performance. No diagnostic establishes the independence of records.",
    )
    body(
        document,
        "**Why not pool the Q–Q plot?** Distinct workflow means can create a mixture. Inspecting groups separately is more relevant to a two-sample mean comparison. The Welch test still relies on assumptions and cannot transform simulated data into real-world evidence.",
    )
    markdown(
        document, (ROOT / "docs/INDUSTRY_BEST_PRACTICES.md").read_text(encoding="utf-8")
    )
    document.add_page_break()
    document.add_heading("9. Conclusion", level=1)
    t = result["welch_test"]
    body(
        document,
        "This assessment demonstrates a complete beginner data-science workflow in a pharmacy-operations context: understanding the question, representing data correctly, writing readable Python, cleaning and validating records, exploring distributions, applying statistical methods and communicating results with evidence.",
    )
    body(
        document,
        f"The verified project contains {len(exercises)} practical exercises, seven labeled EDA figures, an executed notebook with {notebook['executed_cells']} successful code cells and {test_count} passing automated tests. Cleaning reconciles {audit['input_rows']} raw rows to {audit['output_rows']} accepted fictional pharmacies, with rejected records and imputation decisions preserved for review.",
    )
    body(
        document,
        f"The primary observed-outcome comparison estimates Standard minus Barcode-assisted at {t['difference_minutes']:.3f} minutes, with a 95% confidence interval of [{t['ci95_low']:.3f}, {t['ci95_high']:.3f}] minutes. The small p-value demonstrates a Welch procedure on a dataset whose workflow difference was deliberately generated. It does not justify clinical, patient-level or real-business conclusions.",
    )
    body(
        document,
        "The most important professional outcome is traceability: raw inputs, schema definitions, source code, actual outputs, charts, tests and limitations agree. Numerical precision and a significant test are not substitutes for a sound study design, appropriate data access or domain validation.",
    )
    document.add_heading("9.1 Beginner internship learning roadmap", level=2)
    for text in [
        "Practice rebuilding the pipeline from a fresh environment and explain each cleaning decision without relying on memorized code.",
        "Extend the project with approved, non-sensitive data only after writing a data dictionary and identifying the observational unit.",
        "Learn SQL filtering, joins and aggregation; then compare SQL summaries with the Pandas results.",
        "Strengthen confidence intervals, sampling design, missing-data reasoning and visualization communication before adding predictive models.",
        "Use small Git branches, focused commits and reviewed pull requests; never trade credential security for a faster upload.",
    ]:
        body(document, text, "List Bullet")
    body(
        document,
        repository_notice(
            "**Final status:** the Word report and repository contents are prepared for review; no repository location is configured."
        ),
    )
    document.add_page_break()
    document.add_heading("10. References", level=1)
    body(
        document,
        "Authoritative documentation consulted 30 October 2026. Online documentation may describe newer versions than the executed environment; Appendix C and execution_environment.json record the actual versions. All assessment-specific numerical results, test output and figures were generated locally from the included synthetic files.",
    )
    for reference in load("docs/references.json"):
        body(
            document,
            f"**[{reference['id']}] {reference['author']}.** {reference['title']}. Accessed 30 October 2026.",
        )
        p = document.add_paragraph(reference["url"])
        p.paragraph_format.space_after = Pt(2)
        for run in p.runs:
            run.font.size = Pt(8.5)
            run.font.color.rgb = RGBColor.from_string(TEAL)
        p = body(document, "Scope: " + reference["note"] + ".")
        p.paragraph_format.space_after = Pt(8)
    document.add_page_break()
    document.add_heading("Appendix A. Reproduction and GitHub publication", level=1)
    body(
        document,
        "**Complete instructions:** docs/RUN_GUIDE.md and docs/GITHUB_UPLOAD.md. The current repository location is listed on the cover when configured. Commands below show local reproduction and, separately, how to publish another copy. Do not create a duplicate repository merely to update the existing one. Activate a fresh virtual environment first.",
    )
    code(
        document,
        "python -m venv .venv\n# Windows PowerShell: .\\.venv\\Scripts\\Activate.ps1\n# macOS/Linux: source .venv/bin/activate\npython -m pip install -r requirements.txt\npython -m pip install -e . --no-deps\npython scripts/verify_submission.py",
    )
    body(
        document,
        "The full verification recreates only the synthetic sample, reruns lint/analysis/tests/notebook, refreshes documentation and rebuilds the report. It stops on failure. Run timestamps and elapsed times may change; the statistical calculations should reproduce at displayed precision.",
    )
    document.add_heading("A.1 Secure repository creation", level=2)
    for text in [
        "Revoke any token exposed in chat through GitHub Settings → Developer settings → Personal access tokens; inspect account activity. Do not reuse it or send another token to the assistant.",
        "Extract the complete repository ZIP. Upload extracted files and preserve their folder structure, rather than uploading only the ZIP.",
        "On your own computer, use GitHub CLI browser login or GitHub Desktop. Set your actual local commit identity, review staged changes and choose repository visibility deliberately.",
    ]:
        body(document, text, "List Number")
    code(
        document,
        'gh auth login --hostname github.com --git-protocol https --web\ngh auth setup-git\ngit init -b main\n# Set your actual local name/email as explained in docs/GITHUB_UPLOAD.md.\ngit add .\ngit diff --cached --stat\ngit commit -m "Complete data science assessment"\ngh repo create pharmacy-data-science-assessment --private --source=. --remote=origin --push\ngh repo view --json url --jq .url',
    )
    body(
        document,
        "For a new copy, use an unused repository name; choose --public only if permitted and intended. The final command prints the genuine URL after a successful push. The current private repository requires assessor access. The optional configuration is supplied as docs/CI_WORKFLOW_TEMPLATE.yml, not an active workflow; no cloud CI run is claimed. [R8–R10]",
    )
    document.add_page_break()
    document.add_heading("Appendix B. Compact data dictionary", level=1)
    body(
        document,
        "The full machine-readable dictionary is data/data_dictionary.csv; expanded definitions and missing-value rules are in docs/DATA_DICTIONARY.md. CSV does not preserve dtype metadata. The clean table has 21 columns: 13 raw columns, one original-row trace, one workload ratio, five imputation flags and one missing-outcome flag.",
    )
    with (ROOT / "data/data_dictionary.csv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream))
    table(
        document,
        ["Column", "Type / unit", "Meaning and rule"],
        [
            [
                r["column"],
                r["measurement_type"] + " / " + r["unit"],
                r["definition_or_range"] + ". " + r["missing_or_invalid_policy"],
            ]
            for r in rows
        ],
        [1.65, 1.7, 3.4],
    )
    document.add_page_break()
    document.add_heading("Appendix C. Execution evidence and file index", level=1)
    body(document, "**Actual local test run**")
    code(document, tests, output=True)
    lint_path = ROOT / "reports/lint_results.txt"
    if lint_path.exists():
        body(document, "**Actual lint result**")
        code(document, lint_path.read_text(encoding="utf-8"), output=True)
    body(document, "**Notebook verification**")
    table(
        document,
        ["Check", "Recorded result"],
        [
            ["Execution status", notebook["status"]],
            [
                "Code cells executed",
                f"{notebook['executed_cells']} / {notebook['code_cells']}",
            ],
            ["Error outputs", str(notebook["error_outputs"])],
            ["Embedded PNG outputs", str(notebook["embedded_images"])],
            ["Notebook execution time (UTC)", notebook["executed_at_utc"]],
            ["Python version", environment["python"].split()[0]],
            ["Analysis execution time (UTC)", environment["executed_at_utc"]],
        ],
        [2.7, 4.05],
    )
    table(
        document,
        ["Dependency", "Executed version"],
        list(environment["packages"].items()),
        [3.5, 3.25],
    )
    body(document, "**Input/output fingerprints (SHA-256)**")
    code(
        document,
        "RAW:   "
        + environment["raw_sha256"]
        + "\nCLEAN: "
        + environment["clean_sha256"],
    )
    body(
        document,
        "Hashes identify the exact data used; they are not a digital signature or external certification. reports/verification_summary.json records the full verification steps, and reports/submission_manifest.sha256 identifies the final repository files.",
    )
    document.add_heading("C.1 Where to find each implementation", level=2)
    table(
        document,
        ["Path", "Responsibility"],
        [
            [
                "src/pharmacy_ds/generate.py",
                "Deterministic synthetic data and controlled defects",
            ],
            [
                "src/pharmacy_ds/cleaning.py",
                "Schema, normalization, quarantine, imputation and validation",
            ],
            [
                "src/pharmacy_ds/statistics.py",
                "Observed-only summaries, covariance/correlation, Welch and CI",
            ],
            [
                "src/pharmacy_ds/visualization.py",
                "Seven reproducible, labeled PNG figures",
            ],
            [
                "src/pharmacy_ds/pipeline.py",
                "End-to-end orchestration and captured exercise outputs",
            ],
            [
                "tests/",
                "48 local tests in this submission; count is recorded by pytest",
            ],
            [
                "notebooks/01_fundamentals_assessment.ipynb",
                "Executed narrative, 16 practicals and seven embedded images",
            ],
            [
                "scripts/verify_submission.py",
                "Fail-fast local reproduction of the full deliverable set",
            ],
            ["docs/", "Theory, dictionary, findings, references and upload/run guides"],
        ],
        [3.25, 3.5],
    )
    destination = ROOT / "reports/Data_Science_Fundamentals_Assessment.docx"
    document.save(destination)
    # Reopen through python-docx to catch a malformed package immediately.
    reopened = Document(destination)
    print(
        f"Created {destination.name}: {len(reopened.paragraphs)} paragraphs, {len(reopened.tables)} tables, {len(reopened.inline_shapes)} embedded figures."
    )
    return destination


if __name__ == "__main__":
    build_report()
