"""
Week 4 – Data Cleaning and Preparation

Outline
1. Load Week 3 datasets
2. Record starting dataset sizes
3. Convert date fields to datetime
4. Convert numeric fields to numeric types
5. Review missing values
6. Identify and handle invalid numeric values
7. Confirm data types after cleaning
8. Record before and after row counts
9. Save cleaned Week 4 datasets

Deliverables
- sold_week4.csv
- listings_week4.csv
- week4_cleaning_summary.csv
- week4_invalid_numeric_summary.csv
- week4_datatype_summary.csv
"""

import os
import pandas as pd


# Set project folder paths.

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "Outputs")
REPORT_DIR = os.path.join(BASE_DIR, "Reports")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


# Step 1 – Load the Week 3 datasets.
# Week 3 already added the monthly mortgage rate data,
# so these datasets are the starting point for cleaning.

sold = pd.read_csv(
    os.path.join(OUTPUT_DIR, "sold_week3.csv"),
    low_memory=False
)

listings = pd.read_csv(
    os.path.join(OUTPUT_DIR, "listings_week3.csv"),
    low_memory=False
)

print("Week 3 datasets loaded.")
print(
    f"Sold: {sold.shape[0]:,} rows × "
    f"{sold.shape[1]} columns"
)
print(
    f"Listings: {listings.shape[0]:,} rows × "
    f"{listings.shape[1]} columns"
)


# Step 2 – Record the starting row counts.
# These counts will be compared with the final row counts
# so we can document exactly how many records were removed.

sold_rows_before = len(sold)
listings_rows_before = len(listings)


# Step 3 – Convert date fields to datetime.
# Using errors="coerce" converts invalid date values to NaT
# instead of causing the script to fail.

DATE_FIELDS = [
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "ContractStatusChangeDate"
]


def convert_date_fields(df, dataset_name):

    converted_fields = []

    for column in DATE_FIELDS:

        if column in df.columns:

            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            converted_fields.append(column)

    print(
        f"\n{dataset_name} date fields converted:"
    )

    for column in converted_fields:
        print(
            f"{column}: {df[column].dtype}"
        )

    return df


sold = convert_date_fields(
    sold,
    "Sold"
)

listings = convert_date_fields(
    listings,
    "Listings"
)


# Step 4 – Convert analytical numeric fields to numeric types.
# Invalid text values are converted to NaN so they can be
# identified as missing rather than causing calculation errors.

NUMERIC_FIELDS = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt",
    "Latitude",
    "Longitude",
    "rate_30yr_fixed"
]


def convert_numeric_fields(df):

    for column in NUMERIC_FIELDS:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


sold = convert_numeric_fields(sold)
listings = convert_numeric_fields(listings)

print("\nNumeric fields converted.")


# Step 5 – Review missing values.
# Missing values are kept as NaN rather than filled with
# estimated values because there is no reliable basis for
# imputing missing MLS transaction or property information.

def missing_value_summary(df, dataset_name):

    summary = pd.DataFrame({
        "Dataset": dataset_name,
        "Column": df.columns,
        "MissingCount": df.isna().sum().values,
        "MissingPercent": (
            df.isna().sum()
            / len(df)
            * 100
        ).round(2).values
    })

    return summary


sold_missing = missing_value_summary(
    sold,
    "Sold"
)

listings_missing = missing_value_summary(
    listings,
    "Listings"
)

missing_summary = pd.concat(
    [
        sold_missing,
        listings_missing
    ],
    ignore_index=True
)

missing_summary.to_csv(
    os.path.join(
        REPORT_DIR,
        "week4_missing_value_summary.csv"
    ),
    index=False
)

print(
    "Saved week4_missing_value_summary.csv"
)


# Step 6 – Identify invalid numeric values.
# These checks follow the invalid-value rules listed
# in the Weeks 4–5 handbook.

INVALID_RULES = {
    "ClosePrice": "less_than_or_equal_zero",
    "LivingArea": "less_than_or_equal_zero",
    "DaysOnMarket": "less_than_zero",
    "BedroomsTotal": "less_than_zero",
    "BathroomsTotalInteger": "less_than_zero"
}


def count_invalid_values(
    df,
    dataset_name
):

    results = []

    for column, rule in INVALID_RULES.items():

        if column not in df.columns:
            continue

        if rule == "less_than_or_equal_zero":

            invalid_count = (
                df[column] <= 0
            ).sum()

        elif rule == "less_than_zero":

            invalid_count = (
                df[column] < 0
            ).sum()

        results.append({
            "Dataset": dataset_name,
            "Field": column,
            "Rule": rule,
            "InvalidCount": invalid_count
        })

    return pd.DataFrame(results)


sold_invalid_summary = count_invalid_values(
    sold,
    "Sold"
)

listings_invalid_summary = count_invalid_values(
    listings,
    "Listings"
)

invalid_numeric_summary = pd.concat(
    [
        sold_invalid_summary,
        listings_invalid_summary
    ],
    ignore_index=True
)

invalid_numeric_summary.to_csv(
    os.path.join(
        REPORT_DIR,
        "week4_invalid_numeric_summary.csv"
    ),
    index=False
)

print(
    "Saved week4_invalid_numeric_summary.csv"
)


# Step 7 – Handle invalid numeric values.
#
# ClosePrice <= 0 is removed from the sold dataset because
# a sold transaction must have a valid positive close price.
#
# Other invalid numeric values are converted to NaN instead
# of removing the entire record. The property may still be
# useful for analyses that do not depend on that specific field.
#
# Listings do not use ClosePrice as a required transaction field,
# so the ClosePrice removal rule is applied only to sold records.


if "ClosePrice" in sold.columns:

    invalid_close_price = (
        sold["ClosePrice"].notna()
        & (sold["ClosePrice"] <= 0)
    )

    sold_removed_close_price = (
        invalid_close_price.sum()
    )

    sold = sold.loc[
        ~invalid_close_price
    ].copy()

else:

    sold_removed_close_price = 0


# Convert invalid LivingArea values to NaN.

for df in [sold, listings]:

    if "LivingArea" in df.columns:

        df.loc[
            df["LivingArea"] <= 0,
            "LivingArea"
        ] = pd.NA


# Convert negative DaysOnMarket values to NaN.

for df in [sold, listings]:

    if "DaysOnMarket" in df.columns:

        df.loc[
            df["DaysOnMarket"] < 0,
            "DaysOnMarket"
        ] = pd.NA


# Convert negative bedroom values to NaN.

for df in [sold, listings]:

    if "BedroomsTotal" in df.columns:

        df.loc[
            df["BedroomsTotal"] < 0,
            "BedroomsTotal"
        ] = pd.NA


# Convert negative bathroom values to NaN.

for df in [sold, listings]:

    if "BathroomsTotalInteger" in df.columns:

        df.loc[
            df["BathroomsTotalInteger"] < 0,
            "BathroomsTotalInteger"
        ] = pd.NA


print("\nInvalid numeric values handled.")
print(
    f"Sold rows removed for ClosePrice <= 0: "
    f"{sold_removed_close_price:,}"
)


# Step 8 – Confirm final data types.
# This report documents the data types after Week 4 cleaning.

def datatype_summary(
    df,
    dataset_name
):

    return pd.DataFrame({
        "Dataset": dataset_name,
        "Column": df.columns,
        "DataType": (
            df.dtypes
            .astype(str)
            .values
        )
    })


sold_datatypes = datatype_summary(
    sold,
    "Sold"
)

listings_datatypes = datatype_summary(
    listings,
    "Listings"
)

datatype_summary_report = pd.concat(
    [
        sold_datatypes,
        listings_datatypes
    ],
    ignore_index=True
)

datatype_summary_report.to_csv(
    os.path.join(
        REPORT_DIR,
        "week4_datatype_summary.csv"
    ),
    index=False
)

print(
    "Saved week4_datatype_summary.csv"
)


# Step 9 – Record before and after row counts.
# This documents whether cleaning removed any records.

sold_rows_after = len(sold)
listings_rows_after = len(listings)

cleaning_summary = pd.DataFrame({
    "Dataset": [
        "Sold",
        "Listings"
    ],
    "RowsBeforeCleaning": [
        sold_rows_before,
        listings_rows_before
    ],
    "RowsAfterCleaning": [
        sold_rows_after,
        listings_rows_after
    ],
    "RowsRemoved": [
        sold_rows_before - sold_rows_after,
        listings_rows_before - listings_rows_after
    ]
})

cleaning_summary.to_csv(
    os.path.join(
        REPORT_DIR,
        "week4_cleaning_summary.csv"
    ),
    index=False
)

print("\nCleaning Summary")
print(
    cleaning_summary.to_string(
        index=False
    )
)


# Step 10 – Save the cleaned Week 4 datasets.
# Week 5 will use these files for date consistency
# and geographic data quality checks.

sold.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "sold_week4.csv"
    ),
    index=False
)

listings.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "listings_week4.csv"
    ),
    index=False
)

print("\nWeek 4 completed.")
print("Saved Outputs/sold_week4.csv")
print("Saved Outputs/listings_week4.csv")
print(
    "Week 5 will continue with date consistency "
    "and geographic data quality checks."
)