# IDX-Exchange

This repository contains my project work for the IDX Exchange Data Analyst Internship. The project focuses on preparing MLS listing and sold transaction datasets for real estate market analysis and future Tableau dashboard development.

## Project Overview

- **Data Cleaning**: Prepare raw data for reliable analysis
- **Market Analytics**: Engineer key housing market metrics
- **Competitive Intelligence**: Identify top agents and brokerages
- **Dashboard Development**: Build interactive Tableau dashboards
- **Market Insights**: Communicate findings through reports and presentations

## Data Sources

The project uses monthly CRMLS listing and sold datasets provided through the IDX Exchange FTP server.

File naming format:
```
CRMLSListingYYYYMM.csv
CRMLSSoldYYYYMM.csv
```

## Week 1 – Monthly Dataset Aggregation

**Completed:**
- Loaded 30 monthly CRMLS sold files and 30 monthly listing files (January 2024 – June 2026)
- Concatenated monthly files into two combined datasets
- Filtered both datasets to `PropertyType == "Residential"` and saved as:
  - `sold.csv`
  - `listings.csv`

**Key Results**

Sold dataset row count:
- After concatenation: 665,896
- After Residential filter: 448,198

Listings dataset row count:
- After concatenation: 967,809
- After Residential filter: 616,099

## Week 2 – Dataset Structuring and Validation

**Completed:**
- Reviewed unique property types in the unfiltered sold and listings datasets
- Created property type share tables comparing Residential records against other property categories
- Created tables for the Residential-filtered datasets reporting column data types, null counts, missing value percentages, and whether each column exceeds 90% missing
- Created distribution summary tables and histograms/boxplots for key numeric fields to review distributions and identify potential outliers
- Dropped columns with more than 90% missing values and saved the results as:
  - `sold_week2.csv`
  - `listings_week2.csv`

**Key Results**

Sold Dataset Property Type Share:

| Property Type | Percent |
|---|---|
| Residential | 67.31% |
| ResidentialLease | 22.89% |
| Land | 3.22% |
| ManufacturedInPark | 2.70% |
| ResidentialIncome | 2.68% |
| CommercialSale | 0.62% |
| CommercialLease | 0.52% |
| BusinessOpportunity | 0.07% |

Residential properties make up 67.31% of the sold dataset (63.66% of listings). Both datasets were filtered to keep only Residential records.

Missing value summary:
- Sold: 15 columns above 90% null
- Listings: 13 columns above 90% null

These high-missing columns (e.g. `FireplacesTotal`, `TaxAnnualAmount`, `ElementarySchoolDistrict`, `BuilderName`) were dropped from both datasets.

Numeric Distribution Summary (Sold dataset):

| Field | Min | Max | Mean | Median |
|---|---|---|---|---|
| ClosePrice | 0 | 989,500,000 | 1,188,704.04 | 825,000 |
| LivingArea | 0 | 17,021,321 | 1,904.23 | 1,646 |
| DaysOnMarket | -288 | 12,430 | 37.32 | 18 |

Some fields contain invalid or extreme values, such as `ClosePrice = 0`, `LivingArea = 0`, and negative `DaysOnMarket`. These will be flagged or cleaned in the Weeks 4–7 data preparation phases, not in Week 2.

**EDA Findings:**
- Residential share: 67.31% (sold), other property types: 32.69%
- Median close price: $825,000, average close price: $1,188,704.04
- Median days on market: 18, average: 37.32. The distribution is strongly right-skewed — minimum value is -288 and maximum is 12,430, indicating invalid records or extreme outliers to be addressed later
- Homes sold above list price: 40.04%, below list price: 42.58%, at list price: ~17.38%
- Listing date recorded after close date: 68 rows — a data consistency issue to flag in Week 4–5
- Counties with the highest median close prices: Del Norte, San Mateo, Santa Clara, San Francisco, Santa Cruz (note: Del Norte's ranking is likely driven by a small transaction count rather than a genuinely high-priced market — worth verifying before use in a dashboard)

## Week 3 – Mortgage Rate Enrichment

**Completed:**
- Fetched the `MORTGAGE30US` series directly from the St. Louis Federal Reserve FRED CSV endpoint
- Converted the weekly mortgage rate data into monthly averages
- Merged the monthly mortgage rate onto both datasets using a `year_month` key (derived from `CloseDate` for sold, `ListingContractDate` for listings)
- Validated the merge by checking that no rows had missing mortgage rate values after the merge
- Saved the enriched outputs as:
  - `sold_week3.csv`
  - `listings_week3.csv`

**Validation Results**

After merging the mortgage rate data:
- Sold rows with missing mortgage rate: 0 (100% coverage)
- Listings rows with missing mortgage rate: 0 (100% coverage)
- Date range covered: January 2024 – June 2026

Example preview from the sold dataset:
```
    CloseDate year_month  ClosePrice  rate_30yr_fixed
0  2024-01-26    2024-01    240000.0    6.642
1  2024-01-05    2024-01    815000.0    6.642
2  2024-01-05    2024-01    810000.0    6.642
3  2024-01-30    2024-01    858000.0    6.642
4  2024-01-29    2024-01  1890500.0    6.642
```

## How to Run

1. Install dependencies:
```
pip install pandas matplotlib
```
2. Place raw monthly CSV files in a local folder named `Data/`.

Then run the Week 1 script:
```
python3 week1_monthly_dataset_aggregation.py
```
Creates an `Outputs/` folder and saves `sold.csv` and `listings.csv`.

Then run the Week 2 script:
```
python3 week2_dataset_validation.py
```
Creates a `Reports/` folder with property type share reports, missing value reports, numeric summary reports, and distribution charts. Updates `Outputs/sold_week2.csv` and `Outputs/listings_week2.csv`.

Then run the Week 3 script:
```
python3 week3_mortgage_rate_enrichment.py
```
Updates `Outputs/sold_week3.csv` and `Outputs/listings_week3.csv`, and saves mortgage rate data and merge validation reports to `Reports/`.

## Repository Notes

This repository is updated weekly throughout the internship. It includes Python scripts and documentation, but excludes raw MLS data and confidential transaction-level output files (only aggregate summary reports are included).
