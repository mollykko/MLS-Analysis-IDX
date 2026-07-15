"""
Week 3 – Mortgage Rate Enrichment

Contents
1. Load Week 2 datasets
2. Fetch weekly mortgage rates from FRED
3. Convert weekly rates to monthly averages
4. Create year_month join keys
5. Merge mortgage rates
6. Validate merge
7. Save Week 3 outputs

Deliverables
- sold_week3.csv
- listings_week3.csv
- mortgage_monthly.csv
- mortgage_merge_validation.csv
"""

import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "Data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "Outputs")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "Reports")

os.makedirs(REPORT_DIR, exist_ok=True)


# -------------------------------------------------------
# Step 1 – Load Week 2 datasets
# -------------------------------------------------------

sold = pd.read_csv(
    os.path.join(OUTPUT_DIR, "sold_week2.csv"),
    low_memory=False
)

listings = pd.read_csv(
    os.path.join(OUTPUT_DIR, "listings_week2.csv"),
    low_memory=False
)

print("Week 2 datasets loaded.")
print(f"Sold: {sold.shape[0]:,} rows × {sold.shape[1]} columns")
print(f"Listings: {listings.shape[0]:,} rows × {listings.shape[1]} columns")


# -------------------------------------------------------
# Step 2 – Fetch mortgage rate data from FRED
# -------------------------------------------------------

url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"

mortgage = pd.read_csv(url)

print("\nMortgage data downloaded from FRED.")

# Handle FRED column names robustly

date_col = mortgage.columns[0]
rate_col = mortgage.columns[1]

mortgage = mortgage.rename(
    columns={
        date_col: "date",
        rate_col: "rate_30yr_fixed"
    }
)

mortgage["date"] = pd.to_datetime(
    mortgage["date"],
    errors="coerce"
)

mortgage["rate_30yr_fixed"] = pd.to_numeric(
    mortgage["rate_30yr_fixed"],
    errors="coerce"
)

mortgage = mortgage.dropna()

print(f"Weekly observations: {len(mortgage):,}")


# -------------------------------------------------------
# Step 3 – Convert weekly data to monthly averages
# -------------------------------------------------------

mortgage["year_month"] = mortgage["date"].dt.to_period("M")

mortgage_monthly = (
    mortgage
    .groupby("year_month", as_index=False)["rate_30yr_fixed"]
    .mean()
)

#round
mortgage_monthly["rate_30yr_fixed"] = (
    mortgage_monthly["rate_30yr_fixed"]
    .round(3)
)
mortgage_monthly_export = mortgage_monthly.copy()

mortgage_monthly_export["year_month"] = (
    mortgage_monthly_export["year_month"]
    .astype(str)
)

mortgage_monthly_export.to_csv(
    os.path.join(
        REPORT_DIR,
        "mortgage_monthly.csv"
    ),
    index=False
)
print(f"Monthly observations: {len(mortgage_monthly)}")


# -------------------------------------------------------
# Step 4 – Create join keys
# -------------------------------------------------------

sold["CloseDate"] = pd.to_datetime(
    sold["CloseDate"],
    errors="coerce"
)

listings["ListingContractDate"] = pd.to_datetime(
    listings["ListingContractDate"],
    errors="coerce"
)

sold["year_month"] = sold["CloseDate"].dt.to_period("M")

listings["year_month"] = (
    listings["ListingContractDate"]
    .dt.to_period("M")
)
# -------------------------------------------------------
# Step 5 – Merge mortgage rates
# -------------------------------------------------------

sold = sold.merge(
    mortgage_monthly,
    on="year_month",
    how="left"
)

listings = listings.merge(
    mortgage_monthly,
    on="year_month",
    how="left"
)

print("\nMortgage rates merged successfully.")


# -------------------------------------------------------
# Step 6 – Validate merge
# -------------------------------------------------------

sold_null = sold["rate_30yr_fixed"].isnull().sum()
listing_null = listings["rate_30yr_fixed"].isnull().sum()

validation = pd.DataFrame({
    "Dataset": ["Sold", "Listings"],
    "Rows": [len(sold), len(listings)],
    "NullMortgageRates": [sold_null, listing_null],
    "CoveragePercent": [
        round((1 - sold_null / len(sold)) * 100, 2),
        round((1 - listing_null / len(listings)) * 100, 2)
    ],
    "EarliestMonth": [
        sold["year_month"].min(),
        listings["year_month"].min()
    ],
    "LatestMonth": [
        sold["year_month"].max(),
        listings["year_month"].max()
    ]
})

validation.to_csv(
    os.path.join(
        REPORT_DIR,
        "mortgage_merge_validation.csv"
    ),
    index=False
)

print("\nMerge Validation")
print(validation)

if sold_null == 0:
    print("✓ Sold dataset successfully matched all mortgage rates.")
else:
    print(f"⚠ Sold dataset has {sold_null} unmatched records.")

if listing_null == 0:
    print("✓ Listings dataset successfully matched all mortgage rates.")
else:
    print(f"⚠ Listings dataset has {listing_null} unmatched records.")


# -------------------------------------------------------
# Step 7 – Preview enriched datasets
# -------------------------------------------------------

print("\nSold Preview")
print(
    sold[
        [
            "CloseDate",
            "year_month",
            "ClosePrice",
            "rate_30yr_fixed"
        ]
    ].head()
)

print("\nListings Preview")
print(
    listings[
        [
            "ListingContractDate",
            "year_month",
            "ListPrice",
            "rate_30yr_fixed"
        ]
    ].head()
)


# -------------------------------------------------------
# Step 8 – Save Week 3 datasets
# -------------------------------------------------------

sold.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "sold_week3.csv"
    ),
    index=False
)

listings.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "listings_week3.csv"
    ),
    index=False
)

print("\nWeek 3 datasets saved.")
print("sold_week3.csv")
print("listings_week3.csv")

print("\nWeek 3 completed.")