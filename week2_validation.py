import os
import glob
import pandas as pd

# ------------------------------------------------------------
# Week 2 – Dataset Structuring and Validation
#
# This script follows the Week 2–3 internship handbook.
# It starts from the raw monthly MLS files created in Week 1.
# ------------------------------------------------------------


# ------------------------------------------------------------
# Set project folders
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_DIR = os.path.join(BASE_DIR, "Data")
OUTPUT_DIR = os.path.join(BASE_DIR, "Outputs")
REPORT_DIR = os.path.join(BASE_DIR, "Reports")

os.makedirs(REPORT_DIR, exist_ok=True)


# ------------------------------------------------------------
# Load all monthly SOLD files
# ------------------------------------------------------------

print("Loading sold datasets...")

sold_files = sorted(
    glob.glob(
        os.path.join(DATA_DIR, "CRMLSSold*.csv")
    )
)

sold_frames = []

for file in sold_files:

    df = pd.read_csv(file, low_memory=False)

    # Some _filled files contain these two extra columns
    df = df.drop(
        columns=["latfilled", "lonfilled"],
        errors="ignore"
    )

    sold_frames.append(df)

sold = pd.concat(
    sold_frames,
    ignore_index=True
)

print(f"Sold files loaded: {len(sold_files)}")
print(f"Sold rows: {len(sold):,}")


# ------------------------------------------------------------
# Load all monthly LISTING files
# ------------------------------------------------------------

print("\nLoading listing datasets...")

listing_files = sorted(
    glob.glob(
        os.path.join(DATA_DIR, "CRMLSListing*.csv")
    )
)

listing_frames = []

for file in listing_files:

    df = pd.read_csv(file, low_memory=False)

    listing_frames.append(df)

listings = pd.concat(
    listing_frames,
    ignore_index=True
)

print(f"Listing files loaded: {len(listing_files)}")
print(f"Listing rows: {len(listings):,}")


# ------------------------------------------------------------
# Inspect dataset structure
# ------------------------------------------------------------
# Record:
# - row count
# - column count
# - column data type
# - missing values
# ------------------------------------------------------------

print("\nInspecting dataset structure...")

sold_structure = pd.DataFrame({

    "Column": sold.columns,
    "DataType": sold.dtypes.astype(str),
    "NullCount": sold.isnull().sum().values,
    "MissingPercent": (
        sold.isnull().sum() /
        len(sold) * 100
    ).round(2).values

})

sold_structure.to_csv(
    os.path.join(
        REPORT_DIR,
        "sold_structure.csv"
    ),
    index=False
)

listings_structure = pd.DataFrame({

    "Column": listings.columns,
    "DataType": listings.dtypes.astype(str),
    "NullCount": listings.isnull().sum().values,
    "MissingPercent": (
        listings.isnull().sum() /
        len(listings) * 100
    ).round(2).values

})

listings_structure.to_csv(
    os.path.join(
        REPORT_DIR,
        "listings_structure.csv"
    ),
    index=False
)

print("Structure reports created.")


# ------------------------------------------------------------
# Review property types
# ------------------------------------------------------------
# Review the property categories before filtering.
# This answers:
# "What is the Residential vs. other property type share?"
# ------------------------------------------------------------

print("\nReviewing property types...")

sold_property = (
    sold["PropertyType"]
    .value_counts(dropna=False)
    .reset_index()
)

sold_property.columns = [
    "PropertyType",
    "Count"
]

sold_property["SharePercent"] = (
    sold_property["Count"] /
    len(sold) * 100
).round(2)

sold_property.to_csv(
    os.path.join(
        REPORT_DIR,
        "sold_property_types.csv"
    ),
    index=False
)

listing_property = (
    listings["PropertyType"]
    .value_counts(dropna=False)
    .reset_index()
)

listing_property.columns = [
    "PropertyType",
    "Count"
]

listing_property["SharePercent"] = (
    listing_property["Count"] /
    len(listings) * 100
).round(2)

listing_property.to_csv(
    os.path.join(
        REPORT_DIR,
        "listing_property_types.csv"
    ),
    index=False
)

print(sold_property)


# ------------------------------------------------------------
# Filter Residential properties
# ------------------------------------------------------------
# Only Residential properties will be used for
# the remaining analysis.
# ------------------------------------------------------------

print("\nFiltering Residential properties...")

sold = sold[
    sold["PropertyType"] == "Residential"
].copy()

listings = listings[
    listings["PropertyType"] == "Residential"
].copy()

print(f"Residential sold rows: {len(sold):,}")
print(f"Residential listing rows: {len(listings):,}")

# ------------------------------------------------------------
# Missing value analysis
# ------------------------------------------------------------
# Calculate:
# - null count
# - missing percentage
# - columns with more than 90% missing values
# ------------------------------------------------------------

print("\nAnalyzing missing values...")

sold_missing = pd.DataFrame({
    "Column": sold.columns,
    "DataType": sold.dtypes.astype(str),
    "NullCount": sold.isnull().sum().values,
    "MissingPercent": (
        sold.isnull().sum() / len(sold) * 100
    ).round(2).values
})

sold_missing["Over90PercentMissing"] = (
    sold_missing["MissingPercent"] > 90
)

sold_missing.to_csv(
    os.path.join(REPORT_DIR, "sold_missing_value_report.csv"),
    index=False
)

listings_missing = pd.DataFrame({
    "Column": listings.columns,
    "DataType": listings.dtypes.astype(str),
    "NullCount": listings.isnull().sum().values,
    "MissingPercent": (
        listings.isnull().sum() / len(listings) * 100
    ).round(2).values
})

listings_missing["Over90PercentMissing"] = (
    listings_missing["MissingPercent"] > 90
)

listings_missing.to_csv(
    os.path.join(REPORT_DIR, "listings_missing_value_report.csv"),
    index=False
)

print(f"Sold columns >90% missing: {(sold_missing['Over90PercentMissing']).sum()}")
print(f"Listing columns >90% missing: {(listings_missing['Over90PercentMissing']).sum()}")


# ------------------------------------------------------------
# Drop columns with more than 90% missing values
# ------------------------------------------------------------
# Keep the remaining columns for later analysis.
# ------------------------------------------------------------

sold_drop = sold_missing.loc[
    sold_missing["Over90PercentMissing"],
    "Column"
].tolist()

listing_drop = listings_missing.loc[
    listings_missing["Over90PercentMissing"],
    "Column"
].tolist()

sold = sold.drop(columns=sold_drop)

listings = listings.drop(columns=listing_drop)


# ------------------------------------------------------------
# Numeric distribution summary
# ------------------------------------------------------------
# Produce the summary required in the handbook:
# - ClosePrice
# - LivingArea
# - DaysOnMarket
#
# Statistics:
# - minimum
# - maximum
# - mean
# - median
# - percentiles
# ------------------------------------------------------------

print("\nCreating numeric distribution summary...")

numeric_fields = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket"
]

sold_numeric = sold[numeric_fields].apply(
    pd.to_numeric,
    errors="coerce"
)

summary = pd.DataFrame({
    "Minimum": sold_numeric.min(),
    "Maximum": sold_numeric.max(),
    "Mean": sold_numeric.mean().round(2),
    "Median": sold_numeric.median().round(2),
    "25th Percentile": sold_numeric.quantile(0.25),
    "75th Percentile": sold_numeric.quantile(0.75),
    "95th Percentile": sold_numeric.quantile(0.95),
    "99th Percentile": sold_numeric.quantile(0.99)
})

summary.to_csv(
    os.path.join(
        REPORT_DIR,
        "sold_numeric_distribution_summary.csv"
    )
)

print(summary)


# ------------------------------------------------------------
# Suggested EDA questions
# ------------------------------------------------------------
# These results will be written into the README,
# not submitted as separate deliverables.
# ------------------------------------------------------------

print("\nSuggested EDA Questions")

print("\nMedian Close Price")
print(sold_numeric["ClosePrice"].median())

print("\nAverage Close Price")
print(round(sold_numeric["ClosePrice"].mean(),2))

print("\nMedian Days on Market")
print(sold_numeric["DaysOnMarket"].median())

print("\nAverage Days on Market")
print(round(sold_numeric["DaysOnMarket"].mean(),2))


# Homes sold above vs below list price

price = sold[["ClosePrice","ListPrice"]].copy()

price["ClosePrice"] = pd.to_numeric(
    price["ClosePrice"],
    errors="coerce"
)

price["ListPrice"] = pd.to_numeric(
    price["ListPrice"],
    errors="coerce"
)

price = price.dropna()

price = price[
    price["ListPrice"] > 0
]

above = (
    (price["ClosePrice"] > price["ListPrice"]).mean() * 100
)

below = (
    (price["ClosePrice"] < price["ListPrice"]).mean() * 100
)

print(f"\nAbove List Price: {above:.2f}%")
print(f"Below List Price: {below:.2f}%")


# Date consistency

listing_date = pd.to_datetime(
    sold["ListingContractDate"],
    errors="coerce"
)

close_date = pd.to_datetime(
    sold["CloseDate"],
    errors="coerce"
)

date_issue = (
    listing_date > close_date
).sum()

print(f"\nListing date after close date: {date_issue}")


# County median prices

county = sold.copy()

county["ClosePrice"] = pd.to_numeric(
    county["ClosePrice"],
    errors="coerce"
)

county_summary = (
    county
    .groupby("CountyOrParish")["ClosePrice"]
    .median()
    .sort_values(ascending=False)
    .head(10)
)

print("\nTop Counties by Median Close Price")

print(county_summary)


# ------------------------------------------------------------
# Save Week 2 datasets
# ------------------------------------------------------------
# Save the cleaned Residential datasets after removing
# columns with more than 90% missing values.
# ------------------------------------------------------------

sold.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "sold_week2.csv"
    ),
    index=False
)

listings.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "listings_week2.csv"
    ),
    index=False
)

print("\nWeek 2 completed.")
print("Outputs saved successfully.")