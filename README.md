# IDX Exchange – MLS Analytics Project

## Project Overview

This project turns raw monthly MLS listing and sold transaction data (Southern/Central California, CRMLS feed) into clean, analysis-ready datasets that will power Tableau market analytics dashboards. Data is aggregated across months, validated, enriched with national mortgage rate data, and — in later phases — cleaned, feature-engineered, and visualized to surface housing market trends, pricing patterns, and competitive intelligence on top agents and brokerages.

## Objectives

- Prepare raw MLS data for reliable analysis
- Engineer key housing market metrics (price ratios, price per sq ft, days on market)
- Identify top-performing agents and brokerages
- Build interactive Tableau dashboards for market and competitive analysis
- Communicate findings through a market intelligence report and presentation

## Pipeline Structure

| Week | Stage | What it does | Result |
|---|---|---|---|
| 1 | Monthly Dataset Aggregation | Concatenates 30 monthly listing files and 30 monthly sold files, then filters both to `PropertyType == 'Residential'` | 616,099 listings / 448,198 sold rows retained |
| 2 | Dataset Structuring & Validation | Inspects structure and data types, quantifies missing values, drops columns >90% missing (retaining core analytical fields regardless), summarizes numeric distributions, and answers key EDA questions | 13 columns dropped per dataset; EDA complete (price, days on market, list-vs-close pricing, top counties) |
| 3 | Mortgage Rate Enrichment | Fetches the FRED `MORTGAGE30US` weekly series, resamples to monthly averages, and merges onto both datasets using a `year_month` key | 100% match rate, no unmatched months, Jan 2024 – Jun 2026 |

Weeks 4 onward (cleaning, feature engineering, outlier detection, Tableau dashboards, final report) are in progress — see **Next Steps** below.

## Key Results So Far

- **Residential share**: 67.31% of sold transactions and 63.66% of listings are Residential (the rest are lease, land, income, commercial, etc.)
- **Close price**: median $825,000, mean $1,188,704 — the gap reflects a right-skewed market with a small number of very high-value sales
- **Days on market**: median 18 days, mean 37.32 days
- **Pricing dynamics**: 40.04% of homes sold above list price, 42.58% sold below list price
- **Highest median-price counties**: Del Norte, San Mateo, and Santa Clara lead — Del Norte's ranking is likely driven by a small transaction count rather than genuinely being the priciest market, and is worth a sanity check before it appears in any dashboard
- **Mortgage rate enrichment**: 100% coverage on both datasets, spanning January 2024 – June 2026, with no unmatched months after merging

## Issues Encountered & Resolutions

- **Duplicate monthly files**: added a validation step that raises an error if more than one file exists for the same month, to avoid silently double-counting a month's transactions
- **FRED weekly-to-monthly conversion**: mortgage rates are published weekly; these were grouped and averaged into monthly rates before joining, using a `year_month` key built from `CloseDate` (sold) and `ListingContractDate` (listings)
- **High-missing columns**: 13 fields (e.g. `FireplacesTotal`, `TaxAnnualAmount`, `ElementarySchoolDistrict`, `BuilderName`) were dropped from both datasets after exceeding 90% missing values; core analytical fields (price, size, dates, location) were retained regardless of missingness
- **Data quality issues identified for upcoming cleaning phase** (Weeks 4–7), flagged but not yet resolved:
  - Negative `DaysOnMarket` values (as low as -288), indicating a close or status date logged before the listing date
  - Zero or near-zero `ClosePrice`/`ListPrice` values that aren't valid transactions
  - Extreme outliers in `LotSizeAcres`, `BathroomsTotalInteger`, and `LivingArea` (e.g. a recorded lot size in the millions of acres) consistent with data entry errors rather than real properties

These are expected at this stage — the handbook's Week 4–7 phases specifically cover date-consistency flagging, invalid-value handling, and IQR-based outlier detection, so no cleaning has been applied to the data yet beyond the Residential filter and missing-column drops.

## How to Run

1. Install dependencies: `pip install pandas matplotlib`
2. Place monthly `CRMLSListingYYYYMM.csv` and `CRMLSSoldYYYYMM.csv` files in a `Data/` folder (not included in this repo — see Data Note below)
3. Run scripts in order from the project root:
   ```
   python3 Scripts/week1.py
   python3 Scripts/week2_validation_structure.py
   python3 Scripts/week3_mortgage_enrichment.py
   ```
4. Each script reads the previous week's output from `Outputs/` and writes its own results there; supporting reports (missing value summaries, EDA, distributions) are written to `Reports/`

**Data Note**: Raw MLS transaction data is confidential and is not included in this repository, per program requirements.

## Outputs

- `Outputs/listings.csv`, `Outputs/sold.csv` — combined, Residential-filtered datasets (Week 1)
- `Outputs/listings_week2.csv`, `Outputs/sold_week2.csv` — datasets after high-missing column drops (Week 2)
- `Outputs/listings_week3.csv`, `Outputs/sold_week3.csv` — Week 2 datasets enriched with monthly mortgage rates (Week 3)
- `Reports/` — property type summaries, dataset structure reports, missing value reports, numeric distribution and outlier summaries, EDA summary, top counties by median price, mortgage rate data, and merge validation

## Next Steps

- **Weeks 4–5**: Clean and standardize the dataset — fix date types, handle invalid numeric values, add date-consistency and geographic data quality flags
- **Week 6**: Engineer market metrics (price ratio, price per sq ft, days on market, listing-to-contract and contract-to-close durations) and add school district data
- **Week 7**: Apply IQR-based outlier detection and produce a filtered, analysis-ready dataset
- **Weeks 8–10**: Build Tableau market analysis and competitive analysis dashboards
- **Weeks 11–12**: Publish dashboards, write the 1-page market intelligence report, and deliver the final presentation
