# 7. Data analysis results and interpretation

## 7.1 Row accounting and data quality

| Stage | Row count | Explanation |
|---|---|---|
| Raw CSV | 125 | 120 synthetic sites plus 5 exact duplicate records |
| After exact deduplication | 120 | Only identical records were removed |
| Critical rejected records | 3 | One invalid ID, one invalid workflow, one invalid date |
| Valid cleaned sites | 117 | One row per accepted fictional pharmacy |
| Observed wait outcomes | 111 | Required for wait summaries and Welch test |
| Missing wait outcomes | 6 | Five original missing values plus one invalid negative value; not imputed |
| Complete observed workload/wait pairs | 101 | Excludes imputed prescription/staff inputs and absent outcomes |

Three region entries become Unknown (two missing, one unrecognized). Invalid numeric conversion counts and source CSV row numbers are recorded in the audit/rejection files. No raw rows are silently rewritten. The raw-missingness chart counts empty cells, not invalid but non-null strings/numbers; these are distinct quality problems.

## 7.2 Predictor imputation audit

| Column | Imputed cells | Median fill used |
|---|---|---|
| daily_prescriptions | 6 | 147 |
| staff_on_duty | 4 | 4 |
| stock_availability_pct | 4 | 93.26 |
| inventory_value_inr | 3 | 37380.83 |
| expired_units | 0 | 2 |

Counts are filled with rounded whole-number medians. The expiry column required no replacements; its recorded median is a reproducible potential fill value. Boolean flags preserve which entries were estimated. Mean waits are never filled. Stock-risk counts include four imputed stock values and therefore remain descriptive only.

## 7.3 Descriptive statistics and EDA

Among 111 observed site mean waits, the mean is **8.147 minutes** and the median is **8.150 minutes**. Sample variance is **2.732 minutes squared** and sample SD is **1.653 minutes**. Minimum and maximum observed site means are 4.19 and 12.02 minutes; the first and third quartiles are 7.255 and 9.025 minutes.

The IQR-fence exercise flags four possible wait outliers in the pooled distribution; they are retained because an outlier flag is not evidence of a recording error. Inspect them and their workflow context instead of deleting them to change a p-value. The histogram and box plot show distributions of site summaries, not individual waits.

| Workflow | Observed n | Missing waits | Mean (min) | Sample SD (min) | Shapiro p |
|---|---|---|---|---|---|
| Standard | 55 | 2 | 8.678 | 1.309 | 0.7558 |
| Barcode-assisted | 56 | 4 | 7.625 | 1.795 | 0.1247 |

The descriptive stock-risk counts are Low=36, Medium=74 and High=7. Categories are ordered Low < Medium < High and are generated from teaching-only cutoffs. No validated risk or quality claim is implied.

## 7.4 Probability, covariance and correlation

Of the 111 sites with an observed mean wait, 99 have a mean below 10 minutes, giving an empirical probability of **0.8919**. This is a site-level fraction, not the chance that a randomly selected individual waits less than 10 minutes. Unknown waits are excluded from both numerator and denominator.

Using 101 complete observed workload/wait pairs, Pearson r is **0.4842** and sample covariance is **18.6331 (prescriptions per staff member) × minutes**. The positive association means higher workload tends to accompany higher site mean wait in this simulation. It is exploratory, scale-dependent for covariance, and not causal evidence. Workflow may contribute to the pooled relationship.

The separate assumed model X ~ N(10, 2²) gives P(X <= 12)=0.8413 and P(8 <= X <= 12)=0.6827. These model values are not estimates of the observed dataset's normality.

## 7.5 Primary hypothesis test: Welch comparison

**H0:** the two workflow population mean site waits are equal. **H1:** they differ. The prespecified procedure is a two-sided Welch independent-samples t-test at alpha=0.05, comparing **Standard minus Barcode-assisted**. Outcomes are observed only. [R4]

| Test quantity | Executed value |
|---|---|
| Difference in means | 1.054 minutes |
| Standard error of difference | 0.2978 minutes |
| Welch t statistic | 3.5375 |
| Welch-Satterthwaite degrees of freedom | 100.657 |
| Two-sided p-value | 0.000612561 |
| 95% confidence interval | [0.463, 1.644] minutes |
| Decision at alpha=0.05 | Reject H0 |

The interval does not include zero, consistent with the small p-value. In this simulated sample, Standard has a higher mean site wait. This demonstrates the mechanics of comparison, uncertainty and reporting; it does not show that barcode systems improve a real pharmacy.

## 7.6 Assumption checks and limitations

- Each generator record is a distinct fictional pharmacy; duplicates are removed before analysis. Real clustered or repeated-site data would need a design-aware method rather than pretending every row is independent.
- Q-Q plots are examined separately by workflow. Shapiro-Wilk p-values are reported as diagnostics, not proof of normality. Neither group diagnostic rejects normality at 0.05 in this run, but that alone does not establish the assumption. [R5]
- Welch accommodates unequal variances; it does not remove dependence, selection bias, severe anomalies or measurement error.
- Six absent/invalid outcomes are excluded, not replaced. Complete-case analysis can be biased in real observational data. Predictors with imputed values are excluded from the workload correlation, but risk counts intentionally include flagged stock imputations.
- The workflow difference was deliberately built into the outcome-generating formula. Results have no external validity for a real business or patient population and no clinical interpretation.
- One primary mean-comparison test is specified. Correlation is exploratory; normality checks are diagnostics. No broad screening of subgroup p-values or post-hoc causal claims is presented.
- No actual intervention recommendation follows from a fictional dataset. A real study would require an appropriate sampling design, validated measurement definitions, power planning, missingness review and domain oversight.
