"""Publication-style EDA charts with explicit units and sample definitions."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

from pharmacy_ds.config import RISK_LEVELS, WORKFLOWS
from pharmacy_ds.statistics import correlation_sample

PALETTE = {"Standard": "#25466A", "Barcode-assisted": "#008C95"}


def create_figures(raw: pd.DataFrame, df: pd.DataFrame, output: Path) -> list[Path]:
    """Save seven separate figures; do not show a GUI during scripted runs."""
    output.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="notebook", font="DejaVu Sans")
    plt.rcParams.update(
        {
            "axes.spines.top": False,
            "axes.spines.right": False,
            "savefig.facecolor": "white",
            "axes.titleweight": "bold",
        }
    )
    paths = []

    def save(fig, name):
        fig.text(
            0.01,
            0.008,
            "Synthetic educational data • no patient records",
            fontsize=8,
            color="#5A6874",
        )
        fig.tight_layout(rect=(0, 0.035, 1, 1))
        path = output / name
        fig.savefig(
            path,
            dpi=170,
            bbox_inches="tight",
            metadata={"Software": "Pharmacy DS assessment"},
        )
        plt.close(fig)
        paths.append(path)

    y = df["mean_wait_minutes"].dropna()
    fig, ax = plt.subplots(figsize=(8.4, 4.5))
    sns.histplot(y, bins=12, color="#008C95", edgecolor="white", ax=ax)
    ax.axvline(
        y.mean(), color="#C46D30", linestyle="--", label=f"Mean: {y.mean():.2f} min"
    )
    ax.set(
        title=f"Distribution of site mean wait (observed n={len(y)})",
        xlabel="Site mean wait (minutes)",
        ylabel="Number of pharmacies",
    )
    ax.legend(frameon=False)
    save(fig, "01_wait_histogram.png")

    fig, ax = plt.subplots(figsize=(8.4, 4.5))
    sns.boxplot(
        data=df,
        x="workflow",
        y="mean_wait_minutes",
        order=WORKFLOWS,
        hue="workflow",
        palette=PALETTE,
        legend=False,
        ax=ax,
        width=0.45,
    )
    sns.stripplot(
        data=df,
        x="workflow",
        y="mean_wait_minutes",
        order=WORKFLOWS,
        color="#53626E",
        alpha=0.42,
        jitter=False,
        size=3,
        ax=ax,
    )
    ax.set(
        title="Workflow comparison: observed site means only",
        xlabel="Simulated workflow",
        ylabel="Site mean wait (minutes)",
    )
    save(fig, "02_wait_by_workflow.png")

    corr = correlation_sample(df)
    fig, ax = plt.subplots(figsize=(8.4, 4.5))
    sns.scatterplot(
        data=corr,
        x="workload_per_staff",
        y="mean_wait_minutes",
        hue="workflow",
        hue_order=WORKFLOWS,
        palette=PALETTE,
        s=50,
        alpha=0.85,
        ax=ax,
    )
    ax.set(
        title=f"Workload and wait: complete observed inputs (n={len(corr)})",
        xlabel="Daily prescriptions per staff member",
        ylabel="Site mean wait (minutes)",
    )
    ax.legend(title="Workflow", frameon=False, fontsize=8)
    save(fig, "03_workload_scatter.png")

    counts = df["stock_risk"].value_counts(sort=False).reindex(RISK_LEVELS)
    fig, ax = plt.subplots(figsize=(8.4, 4.5))
    bars = ax.bar(
        counts.index, counts.values, color=["#008C95", "#D49A3A", "#B4534E"], width=0.55
    )
    ax.bar_label(bars, padding=3)
    ax.set_ylim(0, counts.max() * 1.18)
    imputed = int(df["stock_availability_pct_was_imputed"].sum())
    ax.set(
        title=f"Derived stock-risk counts (includes {imputed} stock imputations)",
        xlabel="Teaching-only stock-risk category: Low → Medium → High",
        ylabel="Number of pharmacies",
    )
    save(fig, "04_stock_risk_counts.png")

    missing = raw.isna().sum().sort_values()
    fig, ax = plt.subplots(figsize=(8.4, 4.9))
    bars = ax.barh(missing.index, missing.values, color="#25466A")
    ax.bar_label(bars, padding=3, fontsize=8)
    ax.set_xlim(0, max(missing.max() + 1.5, 2))
    ax.set(
        title="Raw-file missing cells before cleaning",
        xlabel="Missing cell count (does not include invalid non-null values)",
    )
    ax.tick_params(axis="y", labelsize=8)
    save(fig, "05_raw_missingness.png")

    # A separate image per workflow avoids pooling distinct distributions.
    for workflow, name in zip(
        WORKFLOWS, ["06_qq_standard.png", "07_qq_barcode.png"], strict=True
    ):
        values = df.loc[df["workflow"].eq(workflow), "mean_wait_minutes"].dropna()
        fig, ax = plt.subplots(figsize=(8.4, 4.5))
        (theoretical, ordered), (slope, intercept, _) = stats.probplot(
            values, dist="norm"
        )
        ax.scatter(theoretical, ordered, color=PALETTE[workflow], s=28, alpha=0.85)
        ax.plot(
            theoretical,
            slope * np.asarray(theoretical) + intercept,
            color="#C46D30",
            linewidth=1.5,
        )
        ax.set(
            title=f"Normal Q–Q diagnostic: {workflow} (n={len(values)})",
            xlabel="Theoretical standard-normal quantile",
            ylabel="Observed site mean wait (minutes)",
        )
        save(fig, name)
    return paths
