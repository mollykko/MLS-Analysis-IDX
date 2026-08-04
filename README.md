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

### Objective

The Week 6 objective was to transform the cleaned Week 5 data into market indicators that can support housing-market analysis and future Tableau dashboards.

The work focused on three areas:

* Engineering pricing, market-speed, and transaction-timeline metrics
* Adding school-district information using property coordinates
* Comparing market conditions across counties

### Engineered Features

The following features were added to both datasets:

| Feature                      | Calculation                                  | Business Purpose                                                            |
| ---------------------------- | -------------------------------------------- | --------------------------------------------------------------------------- |
| Price Ratio                  | `ClosePrice / OriginalListPrice`             | Measures whether properties sold above or below their original asking price |
| Close-to-Original-List Ratio | `ClosePrice / OriginalListPrice`             | Captures the effect of the complete listing and price-reduction history     |
| Price Per Sq Ft              | `ClosePrice / LivingArea`                    | Allows pricing comparisons across differently sized properties              |
| Days on Market               | Existing `DaysOnMarket` field                | Measures how quickly properties move through the market                     |
| Year / Month / YrMo          | Derived from `CloseDate`                     | Supports monthly trend analysis                                             |
| Listing-to-Contract Days     | `PurchaseContractDate - ListingContractDate` | Measures the time required to receive an accepted offer                     |
| Contract-to-Close Days       | `CloseDate - PurchaseContractDate`           | Measures the length of the escrow and closing process                       |

Ratios were calculated only when `OriginalListPrice` was greater than zero, and price per square foot was calculated only when `LivingArea` was greater than zero. Invalid negative transaction durations were converted to missing values while the original records and Week 5 quality flags were retained.

Extreme but otherwise valid values were not removed during Week 6. Statistical outlier treatment will be performed in Week 7.

### Feature Validation

The feature-validation report confirms that no engineered metric contains infinite values.

| Feature                      | Sold Non-Null | Sold Missing | Listings Non-Null | Listings Missing |
| ---------------------------- | ------------: | -----------: | ----------------: | ---------------: |
| Price Ratio                  |       447,369 |          828 |           143,397 |          472,702 |
| Close-to-Original-List Ratio |       447,369 |          828 |           143,397 |          472,702 |
| Price Per Sq Ft              |       447,776 |          421 |           144,126 |          471,973 |
| Days on Market               |       448,147 |           50 |           616,071 |               28 |
| Year                         |       448,197 |            0 |           168,401 |          447,698 |
| Month                        |       448,197 |            0 |           168,401 |          447,698 |
| YrMo                         |       448,197 |            0 |           168,401 |          447,698 |
| Listing-to-Contract Days     |       447,705 |          492 |           286,863 |          329,236 |
| Contract-to-Close Days       |       447,759 |          438 |           168,102 |          447,997 |

The sold dataset has nearly complete feature coverage. The listings dataset contains more missing close-price and close-date-based metrics because many listing records do not represent completed transactions.

### School District Enrichment

School districts were added using the properties’ latitude and longitude values and the California School District Areas 2024–25 boundary shapefile.

The boundary file contains 937 district polygons:

| District Type | Polygon Count |
| ------------- | ------------: |
| Elementary    |           516 |
| Secondary     |            76 |
| Unified       |           345 |
| **Total**     |       **937** |

California’s district boundaries may overlap. A property can belong to one unified district or to separate elementary and secondary districts.

To prevent the spatial join from duplicating MLS records, matches were stored in separate fields:

* `elementary_district_name`
* `elementary_district_code`
* `secondary_district_name`
* `secondary_district_code`
* `unified_district_name`
* `unified_district_code`
* `school_district_match_flag`

Only coordinates that passed the Week 5 geographic-quality checks were eligible for district matching.

#### School District Match Results

| Dataset  | Total Rows | Eligible Coordinates | Ineligible Coordinates | Matched | Unmatched Eligible |
| -------- | ---------: | -------------------: | ---------------------: | ------: | -----------------: |
| Sold     |    448,197 |              431,867 |                 16,330 | 431,740 |                127 |
| Listings |    616,099 |              534,767 |                 81,332 | 534,561 |                206 |

#### Matches by District Type

| Dataset  | Elementary | Secondary | Unified |
| -------- | ---------: | --------: | ------: |
| Sold     |    105,482 |   103,293 | 328,042 |
| Listings |    124,952 |   122,013 | 412,118 |

The spatial join preserved the original row counts for both datasets. The small number of unmatched eligible coordinates may reflect properties located directly on district boundaries, small gaps in the polygon layer, or imprecise source coordinates. These records were retained without forcing a potentially incorrect district assignment.

### County Market Comparison

A segmented summary was created by `CountyOrParish`. The following table highlights the largest and most relevant markets in the dataset.

| County         | Transactions | Median Close Price | Median Price Per Sq Ft | Median Price Ratio | Median Days on Market |
| -------------- | -----------: | -----------------: | ---------------------: | -----------------: | --------------------: |
| Los Angeles    |      111,261 |           $905,000 |                   $609 |              1.000 |                    19 |
| Riverside      |       62,148 |           $600,000 |                   $321 |              0.986 |                    30 |
| San Diego      |       55,610 |           $900,000 |                   $591 |              0.992 |                    15 |
| Orange         |       50,395 |         $1,180,000 |                   $674 |              0.994 |                    14 |
| San Bernardino |       41,586 |           $532,000 |                   $332 |              0.992 |                    24 |
| Alameda        |       21,218 |         $1,140,000 |                   $701 |              1.020 |                    14 |
| Santa Clara    |       19,639 |         $1,600,000 |                   $966 |              1.022 |                    10 |
| San Mateo      |        7,789 |         $1,700,000 |                 $1,052 |              1.013 |                    12 |

### Preliminary Market Insights

* **Santa Clara combined high prices with strong demand.** Its median close price was $1.6 million, its median price per square foot was approximately $966, and properties sold at a median of 102.2% of their original list price. Its median days on market was only 10 days.

* **San Mateo had the highest price per square foot among the major counties shown.** Its median reached approximately $1,052 per square foot, with a median close price of $1.7 million and 12 median days on market.

* **Inland markets were more affordable but generally moved more slowly.** Riverside recorded a $600,000 median close price and approximately $321 per square foot, while properties spent a median of 30 days on the market.

* **Los Angeles and San Diego had similar median close prices but different market speeds.** Los Angeles had a median close price of $905,000 and 19 median days on market, compared with $900,000 and 15 days in San Diego.

* **Alameda and Santa Clara typically closed above their original asking prices.** Their median price ratios were approximately 1.020 and 1.022, while Riverside, San Diego, Orange, and San Bernardino had median ratios below 1.0.

These findings are preliminary. Week 7 outlier analysis will determine whether extreme values materially affect the distributions and segmented comparisons.

### Deliverables

The following Week 6 datasets were created:

* `sold_week6.csv`
* `listings_week6.csv`

The following reports were created:

* `week6_feature_validation_summary.csv`
* `week6_school_district_match_summary.csv`
* `week6_county_market_summary.csv`
* `week6_sample_engineered_metrics.csv`

The sample output demonstrates the engineered metrics at the transaction level and includes examples of both unified districts and overlapping elementary and secondary district assignments.

### Key Result

Week 6 transformed the cleaned MLS records into an analysis-ready dataset containing pricing, market-speed, transaction-duration, time-series, and school-district features. Both datasets retained their original Week 5 row counts, and the newly engineered fields are ready for Week 7 outlier detection and subsequent Tableau development.


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
