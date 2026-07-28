"""
Week 5 – Data Quality Validation

Outline

1. Load Week 4 datasets
2. Date consistency checks
3. Geographic data quality checks
4. Generate validation reports
5. Save Week 5 datasets

Deliverables

- sold_week5.csv
- listings_week5.csv
- week5_date_quality_summary.csv
- week5_geographic_quality_summary.csv
"""



import os
import pandas as pd


# Set project folders.

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "Outputs")
REPORT_DIR = os.path.join(BASE_DIR, "Reports")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


# -------------------------------------------------------
# Step 1 – Load Week 4 datasets.
# Week 4 completed the data cleaning stage.
# Week 5 focuses on validating data quality.
# -------------------------------------------------------

sold = pd.read_csv(
    os.path.join(
        OUTPUT_DIR,
        "sold_week4.csv"
    ),
    low_memory=False
)

listings = pd.read_csv(
    os.path.join(
        OUTPUT_DIR,
        "listings_week4.csv"
    ),
    low_memory=False
)

print("Week 4 datasets loaded.")

print(
    f"Sold: {sold.shape[0]:,} rows × "
    f"{sold.shape[1]} columns"
)

print(
    f"Listings: {listings.shape[0]:,} rows × "
    f"{listings.shape[1]} columns"
)


# -------------------------------------------------------
# Step 2 – Convert date fields.
# These are converted again after loading because
# CSV files do not preserve datetime data types.
# -------------------------------------------------------

DATE_FIELDS = [
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "ContractStatusChangeDate"
]


def convert_dates(df):

    for column in DATE_FIELDS:

        if column in df.columns:

            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

    return df


sold = convert_dates(sold)
listings = convert_dates(listings)

print("\nDate fields converted.")


# -------------------------------------------------------
# Step 3 – Perform date consistency checks.
# These follow the handbook exactly.
# -------------------------------------------------------

def create_date_flags(df):

    if (
        "ListingContractDate" in df.columns
        and "CloseDate" in df.columns
    ):

        df["listing_after_close_flag"] = (
            df["ListingContractDate"]
            >
            df["CloseDate"]
        )

    else:

        df["listing_after_close_flag"] = False


    if (
        "PurchaseContractDate" in df.columns
        and "CloseDate" in df.columns
    ):

        df["purchase_after_close_flag"] = (
            df["PurchaseContractDate"]
            >
            df["CloseDate"]
        )

    else:

        df["purchase_after_close_flag"] = False


    if (
        "ListingContractDate" in df.columns
        and "PurchaseContractDate" in df.columns
        and "CloseDate" in df.columns
    ):

        df["negative_timeline_flag"] = (

            (
                df["PurchaseContractDate"]
                <
                df["ListingContractDate"]
            )

            |

            (
                df["CloseDate"]
                <
                df["PurchaseContractDate"]
            )

        )

    else:

        df["negative_timeline_flag"] = False

    return df


sold = create_date_flags(sold)
listings = create_date_flags(listings)

print("Date consistency flags created.")


# -------------------------------------------------------
# Step 4 – Summarize date quality.
# These summaries will be reported in the README.
# -------------------------------------------------------

date_summary = pd.DataFrame({

    "Dataset": [
        "Sold",
        "Listings"
    ],

    "ListingAfterClose": [

        sold[
            "listing_after_close_flag"
        ].sum(),

        listings[
            "listing_after_close_flag"
        ].sum()

    ],

    "PurchaseAfterClose": [

        sold[
            "purchase_after_close_flag"
        ].sum(),

        listings[
            "purchase_after_close_flag"
        ].sum()

    ],

    "NegativeTimeline": [

        sold[
            "negative_timeline_flag"
        ].sum(),

        listings[
            "negative_timeline_flag"
        ].sum()

    ]

})

date_summary.to_csv(

    os.path.join(

        REPORT_DIR,

        "week5_date_quality_summary.csv"

    ),

    index=False

)

print(
    "Saved week5_date_quality_summary.csv"
)

# -------------------------------------------------------
# Step 5 – Convert coordinate fields to numeric.
# Invalid text values are converted to missing values.
# -------------------------------------------------------

def convert_coordinates(df):

    for column in ["Latitude", "Longitude"]:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


sold = convert_coordinates(sold)
listings = convert_coordinates(listings)

print("\nCoordinate fields converted.")


# -------------------------------------------------------
# Step 6 – Perform geographic data quality checks.
#
# California coordinates should generally fall within:
# Latitude: 32 to 42.1
# Longitude: -124.5 to -114
#
# Records are flagged rather than removed so they can
# still be used for analyses that do not require location.
# -------------------------------------------------------

def create_geographic_flags(df):

    if "Latitude" not in df.columns:
        df["Latitude"] = pd.NA

    if "Longitude" not in df.columns:
        df["Longitude"] = pd.NA

    df["missing_coordinate_flag"] = (
        df["Latitude"].isna()
        | df["Longitude"].isna()
    )

    df["zero_coordinate_flag"] = (
        (df["Latitude"] == 0)
        | (df["Longitude"] == 0)
    )

    df["positive_longitude_flag"] = (
        df["Longitude"] > 0
    ).fillna(False)

    df["implausible_coordinate_flag"] = (
        (
            df["Latitude"].notna()
            & (
                (df["Latitude"] < 32)
                | (df["Latitude"] > 42.1)
            )
        )
        |
        (
            df["Longitude"].notna()
            & (
                (df["Longitude"] < -124.5)
                | (df["Longitude"] > -114)
            )
        )
    )

    df["any_geographic_issue_flag"] = (
        df["missing_coordinate_flag"]
        | df["zero_coordinate_flag"]
        | df["positive_longitude_flag"]
        | df["implausible_coordinate_flag"]
    )

    return df


sold = create_geographic_flags(sold)
listings = create_geographic_flags(listings)

print("Geographic data quality flags created.")


# -------------------------------------------------------
# Step 7 – Summarize geographic data quality.
# -------------------------------------------------------

def geographic_summary(df, dataset_name):

    return {
        "Dataset": dataset_name,
        "Rows": len(df),
        "MissingLatitude": df["Latitude"].isna().sum(),
        "MissingLongitude": df["Longitude"].isna().sum(),
        "MissingCoordinate": df[
            "missing_coordinate_flag"
        ].sum(),
        "ZeroCoordinate": df[
            "zero_coordinate_flag"
        ].sum(),
        "PositiveLongitude": df[
            "positive_longitude_flag"
        ].sum(),
        "ImplausibleCoordinate": df[
            "implausible_coordinate_flag"
        ].sum(),
        "AnyGeographicIssue": df[
            "any_geographic_issue_flag"
        ].sum()
    }


geographic_summary_report = pd.DataFrame([
    geographic_summary(
        sold,
        "Sold"
    ),
    geographic_summary(
        listings,
        "Listings"
    )
])

geographic_summary_report.to_csv(
    os.path.join(
        REPORT_DIR,
        "week5_geographic_quality_summary.csv"
    ),
    index=False
)

print(
    "Saved week5_geographic_quality_summary.csv"
)


# -------------------------------------------------------
# Step 8 – Print the validation results.
# -------------------------------------------------------

print("\nDate Quality Summary")
print(
    date_summary.to_string(
        index=False
    )
)

print("\nGeographic Quality Summary")
print(
    geographic_summary_report.to_string(
        index=False
    )
)


# -------------------------------------------------------
# Step 9 – Save the Week 5 datasets.
#
# The issue flags remain in the datasets so questionable
# records can be filtered when an analysis requires clean
# dates or valid geographic coordinates.
# -------------------------------------------------------

sold.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "sold_week5.csv"
    ),
    index=False
)

listings.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "listings_week5.csv"
    ),
    index=False
)

print("\nWeek 5 completed.")
print("Saved Outputs/sold_week5.csv")
print("Saved Outputs/listings_week5.csv")
print("Saved Reports/week5_date_quality_summary.csv")
print("Saved Reports/week5_geographic_quality_summary.csv")
