# 1. Introduction and assessment objectives

## 1.1 Context and scope
Data science turns data into useful, defensible information through programming, statistics, careful data management and communication. For a B.Pharm student, familiar examples include pharmacy stock monitoring, expiry tracking, prescription workload and service waiting times. This assessment uses those operational ideas without giving treatment, dispensing, dosage or medicine-storage advice.

The practical project investigates one summary observation per fictional pharmacy. It asks: What defects exist in the data? How do site mean waits vary? Is workload associated with waiting? How does a two-sided Welch test compare the two simulated workflows? The purpose is to learn an auditable analytical process, not to prove that a technology works in real pharmacies.

All data are synthetic. The generator creates 120 fictional independent sites and deliberately inserts missing cells, invalid values and five duplicate rows. Real district names provide context only; no business or patient data were collected. The wait-generating formula includes a workflow difference, so a small p-value cannot be interpreted as an external discovery.

## 1.2 Learning objectives
- Use Python variables, basic types, collections, conditions, loops, functions and exception handling.
- Use NumPy arrays and Pandas tables for reliable, readable numerical work.
- Explain mean, median, mode, variance, standard deviation, probability and normal models.
- Distinguish covariance, correlation, effect estimation and hypothesis testing.
- Classify numerical, categorical, nominal, ordinal, discrete, continuous, structured and unstructured data.
- Clean and validate data, document assumptions, conduct EDA and create labeled visualizations.
- Maintain a reproducible repository with tests, documentation, dependency versions and safe Git practices.

## 1.3 Success criteria
Every practical task has runnable Python source and captured output. Cleaning decisions have a machine-readable audit. Charts state units and which records were analyzed. Statistical conclusions identify the observational unit, denominator, missing-value policy and limitations. Automated tests and a fully executed notebook provide evidence instead of invented results.

# 2. Python fundamentals

## 2.1 Variables, values and basic types
A variable is a name referring to an object. Python is dynamically typed: the object has a type, while a name may later refer to a different object. Use descriptive snake_case names such as `stock_units`, not unexplained names such as `x1`. An `int` stores whole counts, a `float` stores approximate real-valued numbers, a `str` stores text, a `bool` stores True/False, and `None` represents the absence of a value. [R1, R7]

Examples include an integer number of expired packs, a floating-point site mean wait, a string pharmacy ID and a Boolean validation flag. Numeric-looking identifiers are still labels. Use explicit conversion such as `int("12")` only after considering validity: `int("twelve")` raises ValueError. Binary floating-point is approximate; use Decimal or integer paise for production accounting rather than treating float arithmetic as exact money.

`=` assigns a value; `==` compares values. Arithmetic operators include `+`, `-`, `*`, `/`, `//`, `%` and `**`. Division with `/` returns a floating-point result. Comparisons such as `<` and `>=` create Boolean values. Scalar Boolean expressions use `and`, `or` and `not`; Pandas elementwise conditions use parenthesized comparisons with `&` or `|`.

## 2.2 Lists, tuples, sets and dictionaries
| Collection | Behavior | Pharmacy-learning example |
|---|---|---|
| List | Ordered, mutable; duplicates allowed; zero-based indexing | A list of stock items or daily observations |
| Tuple | Ordered, immutable sequence; elements may themselves be mutable | A fixed pair of teaching-example bounds |
| Set | Unique, hashable members; no dependable display order | Unique product categories |
| Dictionary | Unique keys mapped to values; insertion order preserved | Item name mapped to units in stock |

A list slice such as `items[:2]` selects the first two elements. Use `.append()` to add one list element. A dictionary lookup uses a key, for example `stock["ORS"]`; `.get()` can supply a default when a key is absent. Sets are valuable for membership and deduplication but should not be used to remove repeated analytical observations without a justified record rule. Sort a set before printing if reproducible display order matters. [R1]

## 2.3 Conditions and loops
`if`, `elif` and `else` choose a path based on conditions. Order matters: first handle a special case such as zero stock, then a low-stock rule. Python uses indentation, conventionally four spaces, to define code blocks. A `for` loop traverses a collection; a `while` loop repeats while a condition is true. Always identify how a while loop will stop. [R1, R7]

`range(3)` yields 0, 1 and 2. `break` exits a loop; `continue` skips to its next iteration. A list comprehension is a compact way to produce a new list, such as low-stock item names. For numerical columns, NumPy vectorization or Pandas column operations are usually clearer than Python loops over individual rows.

## 2.4 Functions and exception handling
A function is a named, reusable operation defined with `def`. Parameters receive inputs; `return` sends a result back to the caller. Local variables belong to the function's scope. Use a docstring to explain purpose, expected inputs, units, outputs and errors. Type hints improve communication and tooling but do not enforce input types by themselves. Avoid mutable default arguments such as an empty list shared between calls. [R1]

Exceptions signal that an operation cannot proceed normally. In a `try` block, attempt a potentially failing operation; `except ValueError` handles that specific error. An `else` block runs when no exception occurs; `finally` runs whether the operation succeeded or failed. Use `raise` to report a meaningful domain validation failure. Do not use a bare `except` or silently ignore unexpected errors. [R1]

The practical inventory function demonstrates negative-input checks. The full analytical pipeline additionally checks finite numbers, valid categories, whole-number counts and column presence. Separating a small teaching example from production-grade validation prevents a beginner from assuming type hints alone make data safe.

## 2.5 NumPy and Pandas basics
NumPy supplies `ndarray` objects and efficient elementwise arithmetic. Most beginner arrays have one numeric dtype; `.shape` describes dimensions. For a two-dimensional array, aggregation along `axis=0` produces column results, while `axis=1` produces row results. Slicing often returns a view, so modifying it may change the original array; use `.copy()` when independence is intended. [R2]

Pandas supplies a one-dimensional labeled Series and a two-dimensional labeled DataFrame. Use `read_csv()` to load a table, `.head()` to inspect rows, `.info()` for schema, `.describe()` for numeric summaries, `.loc` for label/Boolean selection and `.iloc` for positions. `groupby()` summarizes groups. Prefer explicit `.loc` assignment or whole-column assignment over chained indexing. [R3]

Missing values require `.isna()` or `.notna()`, not equality with NaN. `drop_duplicates()` removes duplicate records according to an explicit key; `dropna()` removes selected missing cases; `fillna()` replaces missing values when justified. `to_numeric(errors="coerce")` and `to_datetime(errors="coerce")` expose invalid entries as missing, but this must be audited rather than silently hiding a data-quality problem. CSV files do not retain category ordering or date dtypes; `load_cleaned()` restores these explicitly. [R3]

# 3. Statistical foundations

## 3.1 Populations, samples and the unit of analysis
A population is the full collection of interest; a sample is a subset used to learn about it. A parameter describes a population; a statistic is computed from a sample. This assessment treats each fictional pharmacy as one independent observational unit. The wait column is a site mean, not an individual prescription's wait. Equal weighting of sites is not the same as a prescription-weighted average across all sites.

Descriptive statistics summarize the submitted data. Inferential methods quantify uncertainty under sampling and model assumptions. A simulated dataset can demonstrate inference mechanics, but it cannot establish facts about a real-world population. Real operational studies also require a sampling plan, valid measurement definitions and appropriate ethics and privacy controls.

## 3.2 Mean, median and mode
For observations x1 through xn, the arithmetic mean is `x_bar = sum(xi) / n`. The median is the central sorted value, or the mean of the two central values when n is even. A mode is any most frequent value; data can have one, several or no uniquely informative mode.

For `[2, 4, 4, 4, 5, 5, 7, 9]`, the sum is 40 and n is 8, so the mean is 5. The middle values are 4 and 5, so the median is 4.5. The mode is 4. A few extreme waits can strongly affect a mean, whereas a median is more resistant. For nearly unique continuous observations, report a median or distribution rather than forcing a misleading single mode.

## 3.3 Variance and standard deviation
Population variance divides the squared deviations from the population mean by N. When estimating variation from an independent sample, the usual sample variance is `s^2 = sum((xi - x_bar)^2) / (n - 1)`. The sample SD is `s = sqrt(s^2)`. Variance has squared units, while SD has the units of the original measurement.

In the eight-value example, the squared deviations sum to 32. Treating those eight values as the complete population gives variance 32/8 = 4. Treating them as a sample gives variance 32/7 = 4.571429 and SD approximately 2.138090. NumPy's default is `ddof=0`; use `ddof=1` for sample variance/SD. Pandas Series variance/SD normally default to `ddof=1`; this project still specifies it explicitly. [R2, R3]

SD describes variation between observations. The standard error describes uncertainty of an estimated mean; for independent observations it is estimated by `SE(mean) = s / sqrt(n)`. These are not interchangeable. A large sample can have a precise mean while individual observations still vary widely.

## 3.4 Probability
Probability ranges from 0 to 1. For equally likely outcomes, `P(A) = favorable outcomes / all outcomes`. The complement rule is `P(not A) = 1 - P(A)`. The addition rule is `P(A or B) = P(A) + P(B) - P(A and B)`. Conditional probability is `P(A | B) = P(A and B) / P(B)` when P(B) is positive.

If 3 of 20 fictional packs are damaged, P(damaged) = 3/20 = 0.15. Two draws with replacement have probability (3/20)^2 = 0.0225 of both being damaged, under independent draws. Without replacement the second probability changes, so the probability is (3/20)*(2/19), approximately 0.015789. Independence and mutually exclusive events are different ideas.

An empirical probability uses observed frequencies. Here the event is that a pharmacy's observed mean wait is below 10 minutes, not that an individual person's wait is below 10 minutes. Records with missing outcomes cannot contribute to either the numerator or denominator. A conditional empirical probability restricts the denominator to an observed workflow group.

## 3.5 The normal distribution
A normal distribution is a symmetric, bell-shaped continuous probability model described by mean mu and SD sigma, written `X ~ N(mu, sigma^2)`. In that model the mean, median and mode coincide. Approximately 68.27%, 95.45% and 99.73% of values lie within one, two and three SDs of the mean. [R6]

Standardize a value with `z = (x - mu) / sigma`. For a separate hypothetical model X ~ N(10, 2^2), x = 12 has z = 1. The cumulative probability P(X <= 12) is approximately 0.841345; P(8 <= X <= 12) is approximately 0.682689. These are model calculations, not claims that observed pharmacy waits follow this exact normal distribution.

The height of a probability density is not itself a probability; areas under the density over intervals are probabilities. A continuous model assigns probability zero to any single exact value. Actual waiting-time data may be right-skewed, clustered or nonnegative, so a normal model needs justification. The central limit theorem concerns the sampling distribution of averages under suitable conditions; it does not turn the original observations into normal data. [R6]

## 3.6 Covariance and correlation
Sample covariance is `cov(X,Y) = sum((xi - x_bar)*(yi - y_bar)) / (n - 1)` for paired observations. A positive covariance means above-average X tends to accompany above-average Y; its magnitude depends on the variables' units. Pearson correlation is `r = cov(X,Y) / (sX*sY)` when both SDs are positive. It is unitless and lies between -1 and 1.

Pearson r measures linear association. A near-zero value does not exclude a strong nonlinear relationship. Outliers, confounding, measurement error and pooling distinct groups can distort the association. Spearman rank correlation can be more appropriate for monotonic or ordinal relationships. Neither correlation nor covariance alone proves causation.

This assessment relates daily prescriptions per staff member to site mean wait using only records where the outcome and both workload inputs were observed. It does not treat median-filled predictors as fully observed evidence. The pooled association remains exploratory, because workflow and other variables can contribute to it.

## 3.7 Hypothesis testing and confidence intervals
A hypothesis test compares evidence against a null hypothesis, H0, using a test statistic and a reference distribution under H0. The alternative, H1, states the difference or association of interest. Prespecify the question, outcome, test, comparison direction and alpha rather than choosing them after inspecting p-values.

A p-value is the probability, assuming H0 and the test assumptions, of a test statistic at least as extreme as the observed value. It is not the probability that H0 is true. If p is below alpha, reject H0; otherwise do not reject H0. Failure to reject is not proof of equality. Alpha controls the long-run Type I error rate for the specified procedure under its assumptions; Type II error is failure to detect a specified true effect, and power is 1 minus its probability.

For this project's primary comparison, H0 is equal population mean site waits for Standard and Barcode-assisted workflows; H1 is a difference in either direction. Alpha is 0.05. The independent-samples Welch test uses `t = (mean_A - mean_B) / sqrt(sA^2/nA + sB^2/nB)` and Welch-Satterthwaite degrees of freedom. Unlike a pooled-variance t-test, it does not require equal population variances. [R4]

Important assumptions remain: independent observational units; an outcome with a meaningful mean; no dominant, uninvestigated anomalies; and a sampling distribution for the mean difference that is adequately approximated by the test. Review within-group Q-Q plots and Shapiro-Wilk diagnostics; a large Shapiro p-value does not prove normality, and a diagnostic should not be used as a mechanical test-selection switch. [R5]

A 95% confidence interval is `difference ± t_critical * SE(difference)`. Under repeated suitable sampling, approximately 95% of intervals from that procedure contain the fixed population difference. This is not a 95% probability statement about the already fixed parameter after observing one interval. Report the difference and interval in minutes, not just a p-value. Statistical significance is not clinical or operational importance. Missing outcomes, multiple testing, selection bias and clustered observations can all change valid interpretation. [R4]

# 4. Understanding data types

## 4.1 Measurement types and analytical choices
| Type | Meaning | Example | Suitable beginner summaries |
|---|---|---|---|
| Numerical | Quantities with meaningful arithmetic | Wait minutes; prescription counts | Mean, median, SD, histogram |
| Discrete | Numerical counts with separated possible values | Number of prescriptions or expired packs | Frequency table, count summary |
| Continuous | Conceptual measurements on a continuum, even if rounded | Site mean wait; stock percentage | Histogram, median, mean, SD |
| Categorical | Group membership rather than measured magnitude | Workflow or pharmacy type | Counts, proportions, mode |
| Nominal | Categories without a natural ranking | Region, workflow, pharmacy ID | Counts; do not average labels |
| Ordinal | Categories with a natural order but not equal spacing | Low < Medium < High stock risk | Ordered counts; ranks/median where appropriate |

These distinctions overlap hierarchically: numerical data may be discrete or continuous; categorical data may be nominal or ordinal. They are not eight competing buckets. A Boolean can represent a two-category nominal variable. A date is a temporal variable. A currency amount recorded to paise is technically quantized but is treated as a numerical measurement in this educational analysis.

Do not compute a meaningful average of arbitrarily coded nominal groups. For ordinal categories, the gap from Low to Medium is not guaranteed to equal the gap from Medium to High; coding them 1, 2 and 3 does not make equal spacing true. Use Pandas ordered categories to preserve rank without pretending it is a precise interval scale.

## 4.2 Structured, semi-structured and unstructured data
Structured data follow an explicit row/column schema, as in the assessment CSV or a relational database. Unstructured data include narrative notes, scanned images and audio, whose content lacks a fixed tabular schema. Semi-structured formats, such as JSON with nested keys, contain some organization without requiring a simple rectangular table.

The CSV is structured even though its `notes` cells hold unstructured language. An ID stored as an integer would still be nominal; a continuous measurement stored as text would still be semantically numerical but require parsing. Storage type, measurement type and structural organization answer different questions.

# 5. Dataset design and cleaning methodology

## 5.1 Provenance and study design
The supplied generator uses `numpy.random.default_rng(2026)`. It creates 120 fictional pharmacies with balanced randomized workflow labels before injecting data defects. Each pharmacy appears once before exact duplicate rows are appended. Counts, workload, stock levels and inventory values are simulated; labels that resemble places are contextual, not sampled locations. No personally identifiable or patient-level information is present.

The mean-wait formula is `7.0 + 0.035*(daily_prescriptions/staff_on_duty) - 1.1*(workflow == "Barcode-assisted") + noise`, where the simulated noise is normal with mean 0 and SD 1.35, then rounded to two decimals. This deliberately built-in effect is why results must remain educational. The file retains only the deliberately corrupted input, not a hidden real-world ground truth.

## 5.2 Auditable cleaning decisions
1. Verify that all required raw columns exist; otherwise raise a clear DataValidationError.
2. Preserve the raw CSV and remove only exact duplicate records, not arbitrary repeated category values.
3. Standardize case and whitespace, parse dates and check ID format. Quarantine invalid ID, date or workflow rows; keep rejection reasons and original CSV row numbers.
4. Reject conflicting pharmacy IDs after exact deduplication rather than choosing one untrustworthy record.
5. Convert numeric text, nonfinite values and invalid ranges to missing and count conversions. Prescription and expiry counts must be nonnegative whole numbers; staff must be a positive whole number; observed waits must be positive; stock percentages must be between 0 and 100.
6. Fill only designated non-outcome numeric columns with the valid-data median; round count medians to whole numbers. Keep a Boolean imputation flag per column and record every fill value.
7. Keep unknown regions as Unknown rather than guessing a genuine region. Preserve missing wait outcomes and exclude them only from analyses that require waits.
8. Recalculate workload and teaching-only stock risk from the cleaned inputs; validate ranges, uniqueness and derived-value consistency.

`stock_risk` uses Low for availability >=95%, Medium for 90% to below 95%, and High for below 90%. These arbitrary teaching cutoffs are not validated healthcare quality standards. Four imputed stock values influence the descriptive risk counts; that limitation is disclosed wherever risk counts are used.

## 5.3 Missing-data limitations
Median imputation is simple and resistant to extreme observations, but it can reduce variance and distort associations. It does not recover unknown values. Flagging it improves transparency; it does not remove bias. Outcomes are never imputed for the primary hypothesis test, and the workload correlation excludes records whose workload inputs were imputed.

Missing completely at random means missingness is unrelated to observed or unobserved values; missing at random means dependence can be explained by observed information; missing not at random means it can still depend on the unseen value after conditioning on observed information. These mechanisms cannot be established from a missing-cell count alone. Complete-case analysis may be biased in real studies. The inserted teaching defects should not be used to assert that real pharmacy missingness is harmless.

A real predictive project would fit imputation on training data only and then apply it to validation/test data to avoid leakage. This assessment is descriptive and inferential, not a predictive machine-learning evaluation. The transparent workflow is deliberately more important than adding an unnecessary model.
