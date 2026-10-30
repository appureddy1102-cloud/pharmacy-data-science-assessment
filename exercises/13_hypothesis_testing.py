"""Task 13: two-sided Welch test, confidence interval and normality diagnostics."""

from pharmacy_ds.cleaning import load_cleaned
from pharmacy_ds.config import PROJECT_ROOT
from pharmacy_ds.statistics import analyze

df = load_cleaned(PROJECT_ROOT / "data/processed/pharmacy_operations_clean.csv")
result = analyze(df)
test = result["welch_test"]
print("H0: Standard and Barcode-assisted population mean site waits are equal.")
print("H1: They differ. Prespecified alpha=0.05; two-sided Welch test.")
for name, group in result["workflow_summary"].items():
    print(
        f"{name}: n={group['n']}, mean={group['mean']:.3f}, SD={group['sample_sd']:.3f}"
    )
    print(f"  Shapiro-Wilk W={group['shapiro_w']:.4f}, p={group['shapiro_p']:.4f}")
print(f"Difference (Standard - Barcode-assisted)={test['difference_minutes']:.3f} min")
print(f"95% CI=[{test['ci95_low']:.3f}, {test['ci95_high']:.3f}] min")
print(
    f"Welch t={test['t_statistic']:.4f}; df={test['degrees_of_freedom']:.3f}; p={test['p_value']:.6g}"
)
print(f"Decision: {test['decision']}")
print(
    "Independent simulated sites; no imputed outcomes. Simulation is not clinical evidence."
)
