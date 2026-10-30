# Data dictionary

**Provenance:** generated synthetic pharmacy operations data, seed 2026. No external dataset was collected. One row represents one fictional pharmacy in one snapshot.

The raw table has 13 columns; the clean table adds provenance, a workload ratio, five imputation flags and one missing-outcome flag. CSV does not preserve dtype metadata; use `load_cleaned()`. The numeric dictionary file is in `data/data_dictionary.csv`.

## `pharmacy_id`

- **Measurement type:** Nominal identifier
- **Clean storage type:** string
- **Unit:** none
- **Definition/range:** PH001–PH120 fictional IDs; unique PH plus 3 digits
- **Policy:** Critical: invalid or missing -> quarantine

## `report_date`

- **Measurement type:** Temporal
- **Clean storage type:** datetime64[ns]
- **Unit:** YYYY-MM-DD
- **Definition/range:** Synthetic snapshot 2026-09-30
- **Policy:** Critical: invalid or missing -> quarantine

## `region`

- **Measurement type:** Nominal categorical
- **Clean storage type:** category
- **Unit:** none
- **Definition/range:** Hyderabad; Warangal; Nalgonda; Unknown
- **Policy:** Normalize whitespace/case; missing or unrecognized -> Unknown

## `pharmacy_type`

- **Measurement type:** Nominal categorical
- **Clean storage type:** category
- **Unit:** none
- **Definition/range:** Community; Hospital; Unknown
- **Policy:** Normalize text; unrecognized -> Unknown

## `workflow`

- **Measurement type:** Nominal categorical
- **Clean storage type:** category
- **Unit:** none
- **Definition/range:** Standard; Barcode-assisted
- **Policy:** Normalize text; invalid or missing -> quarantine

## `daily_prescriptions`

- **Measurement type:** Numerical discrete
- **Clean storage type:** int64
- **Unit:** prescriptions per site per day
- **Definition/range:** Nonnegative whole count
- **Policy:** Invalid -> missing; rounded median imputation with flag

## `staff_on_duty`

- **Measurement type:** Numerical discrete
- **Clean storage type:** int64
- **Unit:** staff members at site
- **Definition/range:** Positive whole count
- **Policy:** Invalid -> missing; rounded median imputation with flag

## `mean_wait_minutes`

- **Measurement type:** Numerical continuous outcome
- **Clean storage type:** float64
- **Unit:** minutes (site-level mean)
- **Definition/range:** Positive finite observed values; may remain missing
- **Policy:** Invalid -> missing; NEVER imputed; observed-only analysis

## `stock_availability_pct`

- **Measurement type:** Numerical continuous
- **Clean storage type:** float64
- **Unit:** percent
- **Definition/range:** Finite 0–100
- **Policy:** Invalid -> missing; median imputation with flag

## `inventory_value_inr`

- **Measurement type:** Numerical currency measurement
- **Clean storage type:** float64
- **Unit:** INR
- **Definition/range:** Finite nonnegative illustrative inventory value
- **Policy:** Invalid -> missing; median imputation with flag; not production accounting

## `expired_units`

- **Measurement type:** Numerical discrete
- **Clean storage type:** int64
- **Unit:** units
- **Definition/range:** Nonnegative whole count
- **Policy:** Invalid -> missing; rounded median imputation with flag

## `stock_risk`

- **Measurement type:** Ordinal categorical, derived
- **Clean storage type:** ordered category
- **Unit:** none
- **Definition/range:** Low (>=95%); Medium (>=90% and <95%); High (<90%)
- **Policy:** Recomputed after cleaning; teaching-only thresholds

## `notes`

- **Measurement type:** Unstructured text content within structured CSV
- **Clean storage type:** string
- **Unit:** none
- **Definition/range:** Fictional operational notes; no patient information
- **Policy:** Strip whitespace; missing -> empty string

## `raw_csv_row`

- **Measurement type:** Discrete provenance field, derived
- **Clean storage type:** int64
- **Unit:** 1-based CSV line including header
- **Definition/range:** Original source row; first data row is 2
- **Policy:** Preserved after exact deduplication

## `workload_per_staff`

- **Measurement type:** Numerical continuous ratio, derived
- **Clean storage type:** float64
- **Unit:** prescriptions per staff member per day
- **Definition/range:** daily_prescriptions / staff_on_duty
- **Policy:** Correlation excludes rows with imputed source inputs

## `*_was_imputed`

- **Measurement type:** Binary nominal flags, derived
- **Clean storage type:** bool
- **Unit:** none
- **Definition/range:** One flag for each of 5 designated non-outcome numeric columns
- **Policy:** True iff source numeric value was missing or invalid

## `mean_wait_minutes_missing`

- **Measurement type:** Binary nominal flag, derived
- **Clean storage type:** bool
- **Unit:** none
- **Definition/range:** True iff wait outcome is absent after validation
- **Policy:** No replacement of missing outcome
