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

- **Source:** CRMLS via CoreLogic Trestle API
- **Coverage:** January 2024 – May 2026

### Residential Dataset Size (Week 1)

- Residential listings: **591,977**
- Residential sold transactions: **430,635**

---

## Tools

- Python (pandas)
- Matplotlib
- Tableau

---

# Week 1 — Monthly Dataset Aggregation

## Completed

- Loaded all monthly CRMLS listing files (`CRMLSListing*.csv`) from the `Data/` folder (29 files).
- Loaded all monthly CRMLS sold files (`CRMLSSold*.csv`) from the `Data/` folder, including `_filled` versions (29 files).
- Removed the extra `latfilled` and `lonfilled` columns from `_filled` sold files.
- Combined all monthly files into:
  - `listings.csv`
  - `sold.csv`
- Filtered both datasets to Residential properties only.
- Saved the Residential datasets into the `Outputs/` folder.

## Week 1 Results

### Listings

- Monthly files: **29**
- Rows after concatenation: **930,311**
- Residential rows: **591,977**

### Sold

- Monthly files: **29**
- Rows after concatenation: **640,335**
- Residential rows: **430,635**

---

# Week 2 — Dataset Structuring and Validation

## Completed

- Reloaded all monthly CRMLS listing and sold datasets from the raw `Data/` folder.
- Inspected dataset structure, including:
  - row count
  - column count
  - data types
  - missing values
- Reviewed property types before filtering.
- Calculated Residential property share.
- Filtered both datasets to Residential properties.
- Created missing value reports.
- Flagged columns with more than 90% missing values.
- Removed columns with more than 90% missing values.
- Generated numeric distribution summaries for:
  - ClosePrice
  - LivingArea
  - DaysOnMarket
- Saved cleaned datasets:
  - `sold_week2.csv`
  - `listings_week2.csv`

## Week 2 Results

### Property Type Distribution

Eight property types were identified.

| Property Type | Share |
|--------------|------:|
| Residential | 67.25% |
| ResidentialLease | 22.91% |
| Land | 3.24% |
| ManufacturedInPark | 2.71% |
| ResidentialIncome | 2.68% |
| CommercialSale | 0.62% |
| CommercialLease | 0.52% |
| BusinessOpportunity | 0.07% |

After filtering:

- Residential sold transactions: **430,635**
- Residential listings: **591,977**

### Missing Value Summary

| Dataset | Columns >90% Missing |
|---------|---------------------:|
| Sold | 15 |
| Listings | 13 |

These columns were removed before saving the Week 2 datasets.

### Numeric Distribution Summary

| Metric | ClosePrice | LivingArea | DaysOnMarket |
|-------|-----------:|-----------:|-------------:|
| Minimum | 0 | 0 | -288 |
| Median | 825,000 | 1,644 | 18 |
| Mean | 1,188,983 | 1,904 | 37.34 |
| Maximum | 989,500,000 | 17,021,321 | 12,430 |

The summary statistics indicate that all three variables are right-skewed, with mean values exceeding their medians due to a relatively small number of extreme observations.

## Exploratory Data Analysis

### Residential vs. Other Property Types

Residential properties account for **67.25%** of all sold MLS records.

### Median and Average Close Price

- Median: **$825,000**
- Mean: **$1,188,983**

The mean is substantially higher than the median, indicating a right-skewed price distribution.

### Days on Market

- Median: **18 days**
- Mean: **37.34 days**

Most homes sold relatively quickly, while a smaller number remained on the market much longer.

### Sold Above vs. Below List Price

- Above list price: **40.09%**
- Below list price: **42.54%**

### Date Consistency

A total of **65** records had a ListingContractDate later than the CloseDate. These records should be reviewed during data cleaning.

### Highest Median Price Counties

Among the counties with the highest median sold prices were:

- San Mateo
- Santa Clara
- San Francisco
- Orange
- Marin

---

## Next Steps

The next phase of the project will focus on data cleaning and feature engineering.

Key tasks include:

- Investigate extreme outliers identified during EDA.
- Validate records with inconsistent dates.
- Review zero and negative values for potential data quality issues.
- Engineer additional market metrics, including:
  - Price per square foot
  - Sale-to-list price ratio
  - Monthly market indicators
- Prepare the cleaned analytical dataset for Tableau dashboards and market trend analysis.

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

- sold_week2.csv
- listings_week2.csv

### Reports

- Dataset structure reports
- Property type reports
- Missing value reports
- Numeric distribution summary

---

## Repository Notes

This repository is updated weekly throughout the internship. It contains Python scripts, documentation, and generated reports while excluding the raw MLS datasets from version control.
