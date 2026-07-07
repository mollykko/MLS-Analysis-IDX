# IDX Exchange MLS Analytics

Data analyst internship project analyzing Southern California MLS transaction data from CRMLS (California Regional Multiple Listing Service).

## Overview

This repository contains Python scripts for processing and analyzing monthly MLS listing and sold transaction data. The final deliverable is two interactive Tableau dashboards covering market analysis and competitive intelligence.

## Objectives

- Aggregate monthly MLS listing and sold transaction data into unified datasets
- Clean and validate raw MLS data
- Enrich datasets with 30-year fixed mortgage rate data from FRED
- Engineer housing market metrics including price ratios, price per square foot, and days on market
- Detect and handle outliers using statistical methods
- Build interactive Tableau dashboards for market trend analysis and competitive intelligence
- Produce a one-page market intelligence report and presentation

---

## Data

- Source: CRMLS via CoreLogic Trestle API
- Coverage: January 2024 – May 2026

### Week 1 Residential Datasets

- Residential listings: 591,977 rows
- Residential sold transactions: 430,635 rows

---

## Tools

- Python (pandas, matplotlib)
- Tableau

---

# Week 1 — Monthly Dataset Aggregation

## Completed

- Found and loaded all monthly CRMLS listing files (`CRMLSListing*.csv`) from the `Data/` folder (29 files).
- Found and loaded all monthly CRMLS sold files (`CRMLSSold*.csv`) from the `Data/` folder, including `_filled` versions (29 files).
- Removed the extra `latfilled` and `lonfilled` columns from `_filled` sold files when present.
- Concatenated all monthly files into:
  - `listings.csv`
  - `sold.csv`
- Filtered both datasets to Residential properties only (`PropertyType == "Residential"`).
- Saved the combined Residential datasets to the `Outputs/` folder.

## Week 1 Results

### Listings

- Monthly files loaded: 29
- Rows after concatenation: 930,311
- Residential rows: 591,977

### Sold

- Monthly files loaded: 29
- Rows after concatenation: 640,335
- Residential rows: 430,635

---

# Week 2 — Dataset Structuring and Validation

## Completed

- Reloaded all monthly listing and sold datasets from the raw `Data/` folder.
- Inspected dataset structure, including:
  - row count
  - column count
  - column data types
  - missing values
- Reviewed all property types before filtering.
- Calculated property type distributions and Residential property share.
- Filtered both datasets to Residential properties.
- Created missing value reports showing:
  - data type
  - null count
  - missing percentage
  - columns with more than 90% missing values
- Removed columns with more than 90% missing values.
- Generated numeric distribution summaries for:
  - ClosePrice
  - ListPrice
  - OriginalListPrice
  - LivingArea
  - LotSizeAcres
  - BedroomsTotal
  - BathroomsTotalInteger
  - DaysOnMarket
  - YearBuilt
- Generated histograms and boxplots for each numeric field.
- Answered the exploratory data analysis (EDA) questions provided in the internship handbook.
- Saved cleaned Week 2 datasets:
  - `sold_week2.csv`
  - `listings_week2.csv`

## Week 2 Results

### Property Types

- 8 unique property types identified.
- Residential sold records: 430,635
- Residential listing records: 591,977

### Missing Value Summary

**Sold dataset**

- Columns above 90% missing: 15

**Listings dataset**

- Columns above 90% missing: 13

### Numeric Distribution Highlights

| Field | Median | Mean |
|-------|-------:|------:|
| ClosePrice | $825,000 | $1,188,983 |
| LivingArea | 1,644 sq ft | 1,904 sq ft |
| DaysOnMarket | 18.0 | 37.3 |

### Initial EDA Findings

- Residential property transactions represent the majority of the MLS records.
- DaysOnMarket is strongly right-skewed, with most properties selling within a relatively short period.
- Several numeric fields contain extreme values, including:
  - negative DaysOnMarket values
  - zero ClosePrice values
  - unusually large LivingArea values
- Approximately **40.09%** of homes sold above list price.
- Approximately **42.54%** sold below list price.
- **65** records were identified where the listing date occurred after the close date, indicating potential date consistency issues.
- County-level median sale prices were summarized for further market analysis.

---

## Repository Structure

```
Data/
Outputs/
Reports/
Scripts/
README.md
```

---

## How to Run

Place the raw monthly CRMLS CSV files inside the `Data/` folder.

Run Week 1:

```bash
python week1_listings.py
python week1_sold.py
```

Run Week 2:

```bash
python week2_validation.py
```

Week 2 generates:

### Outputs

- `sold_week2.csv`
- `listings_week2.csv`

---

## Repository Notes

This repository is updated weekly throughout the internship. It contains Python scripts, documentation, and generated reports, while excluding the raw MLS datasets from version control.
