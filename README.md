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
## Week 4 – Data Cleaning and Preparation

### Completed
- Cleaned and standardized the Week 3 mortgage-enriched datasets
- Converted date and numeric fields to appropriate data types
- Identified and handled invalid numeric values while preserving otherwise usable records
- Saved cleaned datasets as `sold_week4.csv` and `listings_week4.csv`

### Key Results

- **Sold:** 448,198 → 448,197 rows; 1 invalid transaction with `ClosePrice <= 0` was removed
- **Listings:** 616,099 → 616,099 rows; no records were removed
- **Invalid LivingArea:** 165 sold records and 394 listing records had `LivingArea <= 0`
- **Negative DaysOnMarket:** 50 sold records and 28 listing records were identified
- No negative bedroom or bathroom counts were found
- Invalid `LivingArea` and `DaysOnMarket` values were converted to missing rather than removing otherwise usable records

## Week 5 – Data Quality Validation

### Completed

- Validated the logical order of listing, purchase contract, and close dates
- Created boolean flags for inconsistent transaction timelines
- Performed geographic data quality checks on latitude and longitude fields
- Generated date and geographic quality summary reports
- Saved validated datasets as:
  - `sold_week5.csv`
  - `listings_week5.csv`

### Key Results

**Date Consistency**

- 68 sold records and 84 listing records had listing dates recorded after close dates
- 240 sold records and 268 listing records had purchase contract dates recorded after close dates
- 533 sold records and 568 listing records contained inconsistent transaction timelines

**Geographic Data Quality**

- 16,231 sold records (3.62%) and 81,009 listing records (13.15%) were missing geographic coordinates
- 37 sold records and 75 listing records contained zero coordinates
- 31 sold records and 85 listing records had positive longitude values (invalid for California)
- 99 sold records and 323 listing records contained implausible coordinates outside the expected California range

The validation process identified records that may not be suitable for every analysis. Rather than removing them, quality flags were added so that future analyses can selectively exclude only the records relevant to each use case.

## Week 6 – Feature Engineering and Market Metrics

### Completed

Engineered the housing market metrics required for future Tableau dashboard development.

Created the following analytical features:

- Price ratio
- Close-to-original-list ratio
- Price per square foot
- Days on market
- Year, month, and year-month variables
- Listing-to-contract duration
- Contract-to-close duration

Added California school-district information using property latitude and longitude coordinates and the California School District Areas 2024–25 boundary dataset.

Because California elementary and secondary district boundaries may overlap, district matches were stored in separate elementary, secondary, and unified district fields. This preserved one row per MLS record while retaining all applicable district information.

Generated a segmented county-level market summary and validation reports for the engineered metrics and school-district matching process.

Saved the enriched datasets as:

- `sold_week6.csv`
- `listings_week6.csv`

### Feature Engineering Results

All engineered numeric features contained zero infinite values.

Sold dataset feature coverage:

| Feature | Non-Null Records | Missing Records |
|---|---:|---:|
| Price Ratio | 447,369 | 828 |
| Close-to-Original-List Ratio | 447,369 | 828 |
| Price Per Sq Ft | 447,776 | 421 |
| Days on Market | 448,147 | 50 |
| Year / Month / YrMo | 448,197 | 0 |
| Listing-to-Contract Days | 447,705 | 492 |
| Contract-to-Close Days | 447,759 | 438 |

The listings dataset contained more missing values for close-price and close-date-based metrics because many listing records did not contain completed transaction information.

### School District Matching Results

| Dataset | Eligible Coordinates | Matched Records | Unmatched Eligible Records |
|---|---:|---:|---:|
| Sold | 431,867 | 431,740 | 127 |
| Listings | 534,767 | 534,561 | 206 |

School-district matching preserved the original dataset row counts:

- Sold: 448,197 rows
- Listings: 616,099 rows

The district boundary file contains unified districts as well as overlapping elementary and secondary district boundaries. Separate district fields were therefore created for each district type.

A small number of eligible coordinates remained unmatched, potentially because points fell directly on district boundaries or within small boundary gaps. These records were retained without forcing a district assignment.

### Segmented Market Summary

Created a county-level summary containing:

- Transaction count
- Median close price
- Median original list price
- Median price ratio
- Median price per square foot
- Median days on market
- Median listing-to-contract days
- Median contract-to-close days

County-level results should be interpreted together with transaction counts because counties with very small samples may produce unstable median values.

## Next Steps

- Apply IQR-based outlier detection to ClosePrice, LivingArea, and DaysOnMarket
- Add outlier flag columns without deleting raw records
- Save both full flagged and clean filtered datasets
- Compare dataset size and median values before and after outlier filtering
- Prepare the final analytical datasets for Tableau dashboard development
- 
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
