
"""
Week 2 – Dataset Structuring and Validation

Contents
1. Load Week 1 datasets
2. Review property types from raw data
3. Inspect dataset structure
4. Analyze missing values
5. Review numeric distributions
6. Perform exploratory data analysis
7. Save Week 2 outputs

Deliverables
- sold_week2.csv
- listings_week2.csv
- Dataset structure reports
- Missing value reports
- Numeric distribution summaries
- EDA summary
"""

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "Data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "Outputs")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "Reports")

os.makedirs(REPORT_DIR, exist_ok=True)


# Core analytical fields should be retained even if they contain missing values.
CORE_FIELDS = {
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt",
    "CloseDate",
    "ListingContractDate",
    "CountyOrParish",
    "PropertyType"
}


# -------------------------------------------------------
# Step 1 – Load Week 1 datasets
# -------------------------------------------------------

listings = pd.read_csv(
    os.path.join(OUTPUT_DIR, "listings.csv"),
    low_memory=False
)

sold = pd.read_csv(
    os.path.join(OUTPUT_DIR, "sold.csv"),
    low_memory=False
)

print("Week 1 datasets loaded.")
print(f"Listings: {listings.shape[0]:,} rows × {listings.shape[1]} columns")
print(f"Sold: {sold.shape[0]:,} rows × {sold.shape[1]} columns")


# -------------------------------------------------------
# Step 2 – Review property types from the raw datasets
# (Week 1 outputs already contain Residential only.)
# -------------------------------------------------------

def property_type_summary(file_pattern, output_name):

    files = sorted(glob.glob(os.path.join(DATA_DIR, file_pattern)))

    frames = []

    for file in files:

        df = pd.read_csv(
            file,
            usecols=["PropertyType"],
            low_memory=False
        )

        frames.append(df)

    property_types = pd.concat(frames, ignore_index=True)

    summary = (
        property_types["PropertyType"]
        .value_counts(dropna=False)
        .rename_axis("PropertyType")
        .reset_index(name="Count")
    )

    summary["SharePercent"] = (
        summary["Count"] /
        summary["Count"].sum() * 100
    ).round(2)

    summary.to_csv(
        os.path.join(REPORT_DIR, output_name),
        index=False
    )

    print(f"Saved {output_name}")

    return summary


sold_property_types = property_type_summary(
    "CRMLSSold*.csv",
    "sold_property_types.csv"
)

listing_property_types = property_type_summary(
    "CRMLSListing*.csv",
    "listings_property_types.csv"
)


# -------------------------------------------------------
# Step 3 – Inspect dataset structure
# -------------------------------------------------------

def dataset_structure(df, output_name):

    structure = pd.DataFrame({

        "Column": df.columns,

        "DataType": df.dtypes.astype(str).values,

        "MissingCount": df.isnull().sum().values,

        "MissingPercent": (
            df.isnull().sum() /
            len(df) * 100
        ).round(2).values

    })

    metadata_keywords = [
        "Latitude",
        "Longitude",
        "ListingKey",
        "Media",
        "Photos",
        "Modification",
        "Originating",
        "Resource"
    ]

    structure["FieldType"] = "Market"

    for keyword in metadata_keywords:

        structure.loc[
            structure["Column"].str.contains(
                keyword,
                case=False,
                na=False
            ),
            "FieldType"
        ] = "Metadata"

    structure.to_csv(
        os.path.join(REPORT_DIR, output_name),
        index=False
    )

    print(f"Saved {output_name}")

    return structure


sold_structure = dataset_structure(
    sold,
    "sold_structure.csv"
)

listing_structure = dataset_structure(
    listings,
    "listings_structure.csv"
)


# -------------------------------------------------------
# Step 4 – Analyze missing values
# -------------------------------------------------------

def missing_value_report(df, output_name, high_missing_output):

    report = pd.DataFrame({

        "Column": df.columns,

        "MissingCount": df.isnull().sum().values,

        "MissingPercent": (
            df.isnull().sum() /
            len(df) * 100
        ).round(2).values

    })

    report["Over90Percent"] = report["MissingPercent"] > 90

    decisions = []

    for _, row in report.iterrows():

        if row["Column"] in CORE_FIELDS:

            decisions.append("Retain Core Field")

        elif row["Over90Percent"]:

            decisions.append("Drop")

        else:

            decisions.append("Retain")

    report["Decision"] = decisions

    report.to_csv(
        os.path.join(REPORT_DIR, output_name),
        index=False
    )

    report[
        report["Over90Percent"]
    ].to_csv(
        os.path.join(REPORT_DIR, high_missing_output),
        index=False
    )

    print(f"Saved {output_name}")

    return report


sold_missing = missing_value_report(
    sold,
    "sold_missing_value_report.csv",
    "sold_columns_over90.csv"
)

listing_missing = missing_value_report(
    listings,
    "listings_missing_value_report.csv",
    "listings_columns_over90.csv"
)


# Drop non-core columns with more than 90% missing values.

sold = sold.drop(
    columns=sold_missing.loc[
        sold_missing["Decision"] == "Drop",
        "Column"
    ],
    errors="ignore"
)

listings = listings.drop(
    columns=listing_missing.loc[
        listing_missing["Decision"] == "Drop",
        "Column"
    ],
    errors="ignore"
)

print(f"Sold columns after cleaning: {sold.shape[1]}")
print(f"Listings columns after cleaning: {listings.shape[1]}")

# -------------------------------------------------------
# Step 5 – Review numeric distributions
# -------------------------------------------------------

NUMERIC_FIELDS = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt"
]


def numeric_distribution(df, dataset_name):

    summary = []
    outliers = []

    for column in NUMERIC_FIELDS:

        if column not in df.columns:
            continue

        series = pd.to_numeric(df[column], errors="coerce").dropna()

        if series.empty:
            continue

        stats = {
            "Field": column,
            "Count": len(series),
            "Minimum": series.min(),
            "5%": series.quantile(0.05),
            "25%": series.quantile(0.25),
            "Median": series.median(),
            "Mean": round(series.mean(), 2),
            "75%": series.quantile(0.75),
            "95%": series.quantile(0.95),
            "Maximum": series.max()
        }

        summary.append(stats)

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outlier_count = ((series < lower) | (series > upper)).sum()

        outliers.append({
            "Field": column,
            "LowerBound": lower,
            "UpperBound": upper,
            "OutlierCount": outlier_count
        })

        # Histogram

        plt.figure(figsize=(7,4))
        plt.hist(series, bins=50)
        plt.title(f"{dataset_name} - {column}")
        plt.xlabel(column)
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(
            os.path.join(
                REPORT_DIR,
                f"{dataset_name}_{column}_histogram.png"
            )
        )
        plt.close()

        # Additional log-scale histogram for highly skewed variables

        if column in [
            "ClosePrice",
            "ListPrice",
            "OriginalListPrice",
            "LivingArea",
            "LotSizeAcres"
        ]:

            positive = series[series > 0]

            if len(positive) > 0:

                plt.figure(figsize=(7,4))
                plt.hist(positive, bins=50)
                plt.xscale("log")
                plt.title(f"{dataset_name} - {column} (Log Scale)")
                plt.xlabel(column)
                plt.ylabel("Frequency")
                plt.tight_layout()
                plt.savefig(
                    os.path.join(
                        REPORT_DIR,
                        f"{dataset_name}_{column}_histogram_log.png"
                    )
                )
                plt.close()

        # Boxplot

        plt.figure(figsize=(7,2))
        plt.boxplot(series, vert=False)
        plt.title(f"{dataset_name} - {column}")
        plt.tight_layout()
        plt.savefig(
            os.path.join(
                REPORT_DIR,
                f"{dataset_name}_{column}_boxplot.png"
            )
        )
        plt.close()

    summary = pd.DataFrame(summary)
    outliers = pd.DataFrame(outliers)

    summary.to_csv(
        os.path.join(
            REPORT_DIR,
            f"{dataset_name}_numeric_distribution_summary.csv"
        ),
        index=False
    )

    outliers.to_csv(
        os.path.join(
            REPORT_DIR,
            f"{dataset_name}_outlier_summary.csv"
        ),
        index=False
    )

    print(f"Saved {dataset_name} numeric reports.")

    return summary


sold_numeric = numeric_distribution(sold, "sold")
listing_numeric = numeric_distribution(listings, "listings")


# -------------------------------------------------------
# Step 6 – Exploratory Data Analysis
# -------------------------------------------------------

eda = {}

# Residential property share

eda["Residential Share (%)"] = round(
    sold_property_types.loc[
        sold_property_types["PropertyType"] == "Residential",
        "SharePercent"
    ].iloc[0],
    2
)

# Close price statistics

eda["Median Close Price"] = sold["ClosePrice"].median()

eda["Mean Close Price"] = round(
    sold["ClosePrice"].mean(),
    2
)

# Days on Market

eda["Median Days on Market"] = sold["DaysOnMarket"].median()

eda["Mean Days on Market"] = round(
    sold["DaysOnMarket"].mean(),
    2
)

# Sold above vs. below list price

eda["Above List Price (%)"] = round(
    (sold["ClosePrice"] > sold["ListPrice"]).mean() * 100,
    2
)

eda["Below List Price (%)"] = round(
    (sold["ClosePrice"] < sold["ListPrice"]).mean() * 100,
    2
)

# Date consistency

sold["CloseDate"] = pd.to_datetime(
    sold["CloseDate"],
    errors="coerce"
)

sold["ListingContractDate"] = pd.to_datetime(
    sold["ListingContractDate"],
    errors="coerce"
)

eda["Listing Date After Close Date"] = (
    sold["ListingContractDate"] >
    sold["CloseDate"]
).sum()

# Highest median price counties

county_summary = (
    sold.groupby("CountyOrParish")["ClosePrice"]
    .median()
    .sort_values(ascending=False)
    .head(10)
)

county_summary.to_csv(
    os.path.join(
        REPORT_DIR,
        "highest_median_price_counties.csv"
    )
)

# Save EDA summary

pd.DataFrame(
    eda.items(),
    columns=["Metric", "Value"]
).to_csv(
    os.path.join(
        REPORT_DIR,
        "week2_eda_summary.csv"
    ),
    index=False
)

print("\nTop Counties by Median Close Price")
print(county_summary)

print("\nEDA Summary")

for metric, value in eda.items():
    print(f"{metric}: {value}")


# -------------------------------------------------------
# Step 7 – Save Week 2 datasets
# -------------------------------------------------------

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

print("\nWeek 2 datasets saved.")
print("sold_week2.csv")
print("listings_week2.csv")

print("\nWeek 2 completed.")