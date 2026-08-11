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


## Week 7 – Outlier Detection and Data Quality

### Objective

Week 7 identified extreme values that could distort market comparisons and Tableau results.

The analysis applied the Interquartile Range method to:

* `ClosePrice`
* `LivingArea`
* `DaysOnMarket`
* `price_per_sqft`
* `close_to_original_list_ratio`

The first three fields are explicitly required by the Week 7 deliverable. Price per square foot and close-to-original-list ratio were also included because extreme values in these Week 6 metrics can distort pricing and negotiation analysis.

All records were preserved in full flagged datasets. Separate filtered datasets were created for downstream analysis.

### Method

IQR thresholds were calculated independently for the sold and listings datasets:

```text
IQR = Q3 - Q1
Lower Bound = Q1 - 1.5 × IQR
Upper Bound = Q3 + 1.5 × IQR
```

A record was classified as an IQR outlier when a non-missing value fell below the lower bound or above the upper bound.

The script also retained the following business rules:

| Field        | Business Rule                              |
| ------------ | ------------------------------------------ |
| ClosePrice   | Values less than or equal to 0 are invalid |
| LivingArea   | Values less than or equal to 0 are invalid |
| DaysOnMarket | Negative values are invalid                |

No additional business-invalid records were found because these values had already been handled during Week 4. Missing values were retained and were not classified as outliers.

### IQR Boundaries

#### Sold Dataset

| Field                        |      Q1 |  Median |        Q3 | Lower Bound | Upper Bound |
| ---------------------------- | ------: | ------: | --------: | ----------: | ----------: |
| ClosePrice                   | 575,000 | 825,000 | 1,300,000 |    -512,500 |   2,387,500 |
| LivingArea                   |   1,248 |   1,646 |     2,224 |        -216 |       3,688 |
| DaysOnMarket                 |       8 |      18 |        48 |         -52 |         108 |
| Price Per Sq Ft              |  367.99 |  537.21 |    732.48 |     -178.76 |    1,279.23 |
| Close-to-Original-List Ratio |  0.9537 |  0.9956 |    1.0193 |      0.8553 |      1.1178 |

#### Listings Dataset

| Field                        |      Q1 |  Median |        Q3 | Lower Bound |  Upper Bound |
| ---------------------------- | ------: | ------: | --------: | ----------: | -----------: |
| ClosePrice                   | 600,000 | 858,000 | 1,355,999 | -533,998.50 | 2,489,997.50 |
| LivingArea                   |   1,248 |   1,673 |     2,304 |        -336 |        3,888 |
| DaysOnMarket                 |       5 |      10 |        21 |         -19 |           45 |
| Price Per Sq Ft              |  396.27 |  565.22 |    767.42 |     -160.47 |     1,324.16 |
| Close-to-Original-List Ratio |  0.9680 |  1.0000 |    1.0283 |      0.8775 |       1.1188 |

Because price, living area, DaysOnMarket, and PPSF are right-skewed nonnegative fields, their IQR lower bounds fall below zero. As a result, most IQR flags for these fields are upper-tail outliers. The percentile values were retained in the detailed report to support further review rather than automatically creating additional removal rules.

### Outlier Results

Individual outlier counts overlap because one record may be extreme in multiple fields.

| Metric                       | Sold Outliers | Sold Percent | Listings Outliers | Listings Percent |
| ---------------------------- | ------------: | -----------: | ----------------: | ---------------: |
| ClosePrice                   |        33,538 |        7.48% |            10,627 |            1.72% |
| LivingArea                   |        19,580 |        4.37% |            30,329 |            4.92% |
| DaysOnMarket                 |        34,211 |        7.63% |            49,203 |            7.99% |
| Price Per Sq Ft              |        18,912 |        4.22% |             6,618 |            1.07% |
| Close-to-Original-List Ratio |        42,545 |        9.49% |            14,869 |            2.41% |

Close-to-original-list ratio produced the largest number of sold outliers, while DaysOnMarket produced the largest number of listing outliers.

The flagged sample confirms that many records were extreme across multiple measures. Examples included multimillion-dollar properties with unusually large living areas, long marketing periods, high price per square foot, and unusually low close-to-original-list ratios.

### Dataset Size Comparison

| Dataset  | Rows Before | Rows After | Unique Rows Excluded | Percent Excluded |
| -------- | ----------: | ---------: | -------------------: | ---------------: |
| Sold     |     448,197 |    344,870 |              103,327 |           23.05% |
| Listings |     616,099 |    521,686 |               94,413 |           15.32% |

The original Week 6 row counts remain intact in:

* `sold_week7_flagged.csv`
* `listings_week7_flagged.csv`

Only the separate filtered datasets exclude records carrying at least one Week 7 outlier flag.

### Median Comparison

#### Sold Dataset

| Metric                       | Before Filtering | After Filtering |   Change |
| ---------------------------- | ---------------: | --------------: | -------: |
| ClosePrice                   |         $825,000 |        $770,000 | -$55,000 |
| LivingArea                   |            1,646 |           1,582 |      -64 |
| DaysOnMarket                 |               18 |              16 |       -2 |
| Price Per Sq Ft              |          $537.21 |         $516.10 |  -$21.11 |
| Close-to-Original-List Ratio |           0.9956 |          1.0000 |  +0.0044 |

#### Listings Dataset

| Metric                       | Before Filtering | After Filtering |   Change |
| ---------------------------- | ---------------: | --------------: | -------: |
| ClosePrice                   |         $858,000 |        $800,000 | -$58,000 |
| LivingArea                   |            1,673 |           1,620 |      -53 |
| DaysOnMarket                 |               10 |               9 |       -1 |
| Price Per Sq Ft              |          $565.22 |         $542.36 |  -$22.86 |
| Close-to-Original-List Ratio |           1.0000 |          1.0000 |   0.0000 |

### Key Findings

* Outlier filtering reduced the sold median close price from $825,000 to $770,000, showing that high-value transactions raised the unfiltered market median.
* The listings median close price decreased from $858,000 to $800,000 after filtering.
* Median living area and price per square foot declined in both datasets, consistent with the removal of unusually large or expensive properties.
* Median DaysOnMarket decreased from 18 to 16 days for sold records and from 10 to 9 days for listings.
* The filtered sold close-to-original-list ratio moved to 1.0, representing a typical transaction closing at its original asking price.
* Because more than one-fifth of sold records were flagged across the five combined metrics, the full flagged dataset should remain available for analyses where luxury or other atypical market segments are relevant.

### Deliverables

The following Week 7 datasets were created:

* `sold_week7_flagged.csv`
* `listings_week7_flagged.csv`
* `sold_week7_filtered.csv`
* `listings_week7_filtered.csv`

The following reports were created:

* `week7_iqr_bounds_summary.csv`
* `week7_outlier_summary.csv`
* `week7_before_after_summary.csv`
* `week7_outlier_sample.csv`

### Key Result

Week 7 produced two versions of each dataset for different analytical purposes:

* The full flagged datasets preserve every record and make each outlier decision auditable.
* The filtered datasets remove records flagged by the IQR thresholds and are prepared for general-market analysis and Tableau dashboard development.

Extreme properties were not permanently deleted, allowing future analyses to include or exclude them depending on the business question.

## Next Steps

- Import the filtered Week 7 datasets into Tableau
- Build monthly market metrics from January 2024 through June 2026
- Add geographic and PropertySubType filters
- Develop the market analysis dashboards
- Develop agent and brokerage competitive-intelligence dashboards
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
