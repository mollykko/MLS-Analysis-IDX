"""
Week 7 - Outlier Detection and Data Quality

Inputs:
- Outputs/sold_week6.csv
- Outputs/listings_week6.csv

Outputs:
- Full datasets with outlier flags
- Separate filtered analysis datasets
- IQR boundary report
- Outlier count report
- Before/after median comparison
- Sample flagged records

Missing values are retained and are not classified as outliers.
"""

from pathlib import Path

import pandas as pd


# -------------------------------------------------------
# Step 1 - Set project folders
# -------------------------------------------------------

# Script is stored inside the Scripts folder.
BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "Outputs"
REPORT_DIR = BASE_DIR / "Reports"

SOLD_INPUT = OUTPUT_DIR / "sold_week6.csv"
LISTINGS_INPUT = OUTPUT_DIR / "listings_week6.csv"

SOLD_FLAGGED_OUTPUT = (
    OUTPUT_DIR / "sold_week7_flagged.csv"
)

LISTINGS_FLAGGED_OUTPUT = (
    OUTPUT_DIR / "listings_week7_flagged.csv"
)

SOLD_FILTERED_OUTPUT = (
    OUTPUT_DIR / "sold_week7_filtered.csv"
)

LISTINGS_FILTERED_OUTPUT = (
    OUTPUT_DIR / "listings_week7_filtered.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# -------------------------------------------------------
# Step 2 - Define fields for outlier detection
# -------------------------------------------------------

# The first three fields are explicitly required by
# the Week 7 deliverable.
#
# Price per square foot and close-to-original-list ratio
# are also included because the handbook identifies them
# as metrics that can distort market analysis.
#
# price_ratio is not included separately because it is
# identical to close_to_original_list_ratio in Week 6.

OUTLIER_FIELDS = {
    "ClosePrice": "close_price",
    "LivingArea": "living_area",
    "DaysOnMarket": "days_on_market",
    "price_per_sqft": "price_per_sqft",
    "close_to_original_list_ratio":
        "close_to_original_list_ratio",
}


# -------------------------------------------------------
# Step 3 - Validate required files and columns
# -------------------------------------------------------

def validate_required_files():

    required_files = [
        SOLD_INPUT,
        LISTINGS_INPUT,
    ]

    missing_files = [
        str(path)
        for path in required_files
        if not path.exists()
    ]

    if missing_files:

        formatted = "\n".join(
            f"- {path}"
            for path in missing_files
        )

        raise FileNotFoundError(
            "The following required files are missing:\n"
            f"{formatted}"
        )


def require_columns(
    df,
    dataset_name
):

    missing_columns = [
        column
        for column in OUTLIER_FIELDS
        if column not in df.columns
    ]

    if missing_columns:

        raise KeyError(
            f"{dataset_name} is missing required columns: "
            f"{missing_columns}"
        )


def convert_numeric_fields(df):

    df = df.copy()

    for column in OUTLIER_FIELDS:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


# -------------------------------------------------------
# Step 4 - Apply business-rule checks
# -------------------------------------------------------

def create_business_invalid_flag(
    series,
    column
):

    # ClosePrice and LivingArea must be positive.
    if column in [
        "ClosePrice",
        "LivingArea",
    ]:

        return (
            series.notna()
            &
            (series <= 0)
        )

    # DaysOnMarket cannot be negative.
    if column == "DaysOnMarket":

        return (
            series.notna()
            &
            (series < 0)
        )

    # The Week 6 derived metrics are evaluated using IQR.
    return pd.Series(
        False,
        index=series.index
    )


# -------------------------------------------------------
# Step 5 - Calculate IQR and create flags
# -------------------------------------------------------

def apply_outlier_flags(
    df,
    dataset_name
):

    df = df.copy()

    bounds_rows = []
    summary_rows = []
    combined_flag_columns = []

    for column, prefix in OUTLIER_FIELDS.items():

        series = df[column]

        business_invalid_flag = (
            create_business_invalid_flag(
                series,
                column
            )
        )

        # Business-invalid values should not influence
        # the IQR boundaries.
        valid_for_iqr = series.mask(
            business_invalid_flag
        )

        valid_values = (
            valid_for_iqr.dropna()
        )

        if valid_values.empty:

            raise ValueError(
                f"{dataset_name} {column} contains "
                "no usable values for IQR."
            )

        q1 = valid_values.quantile(0.25)
        median = valid_values.quantile(0.50)
        q3 = valid_values.quantile(0.75)

        iqr = q3 - q1

        lower_bound = (
            q1 - 1.5 * iqr
        )

        upper_bound = (
            q3 + 1.5 * iqr
        )

        iqr_outlier_flag = (
            valid_for_iqr.notna()
            &
            (
                (valid_for_iqr < lower_bound)
                |
                (valid_for_iqr > upper_bound)
            )
        )

        combined_outlier_flag = (
            business_invalid_flag
            |
            iqr_outlier_flag
        )

        business_flag_column = (
            f"{prefix}_business_invalid_flag"
        )

        iqr_flag_column = (
            f"{prefix}_iqr_outlier_flag"
        )

        combined_flag_column = (
            f"{prefix}_outlier_flag"
        )

        df[business_flag_column] = (
            business_invalid_flag.astype(bool)
        )

        df[iqr_flag_column] = (
            iqr_outlier_flag.astype(bool)
        )

        df[combined_flag_column] = (
            combined_outlier_flag.astype(bool)
        )

        combined_flag_columns.append(
            combined_flag_column
        )

        bounds_rows.append({
            "Dataset": dataset_name,
            "Field": column,
            "NonNullCount":
                int(valid_values.count()),
            "Minimum":
                valid_values.min(),
            "P01":
                valid_values.quantile(0.01),
            "P05":
                valid_values.quantile(0.05),
            "Q1":
                q1,
            "Median":
                median,
            "Q3":
                q3,
            "P95":
                valid_values.quantile(0.95),
            "P99":
                valid_values.quantile(0.99),
            "Maximum":
                valid_values.max(),
            "IQR":
                iqr,
            "LowerBound":
                lower_bound,
            "UpperBound":
                upper_bound,
        })

        summary_rows.append({
            "Dataset": dataset_name,
            "Field": column,
            "TotalRows":
                len(df),
            "MissingValues":
                int(series.isna().sum()),
            "BusinessInvalidCount":
                int(
                    business_invalid_flag.sum()
                ),
            "IQROutlierCount":
                int(
                    iqr_outlier_flag.sum()
                ),
            "TotalFieldOutlierCount":
                int(
                    combined_outlier_flag.sum()
                ),
            "PercentFlagged":
                round(
                    combined_outlier_flag.mean()
                    * 100,
                    2
                ),
        })

    # One record can be an outlier in several fields.
    df["any_week7_outlier_flag"] = (
        df[
            combined_flag_columns
        ]
        .any(axis=1)
    )

    df["week7_outlier_field_count"] = (
        df[
            combined_flag_columns
        ]
        .sum(axis=1)
        .astype("Int64")
    )

    bounds_summary = pd.DataFrame(
        bounds_rows
    )

    outlier_summary = pd.DataFrame(
        summary_rows
    )

    outlier_summary[
        "RowsWithAnyWeek7Outlier"
    ] = int(
        df[
            "any_week7_outlier_flag"
        ].sum()
    )

    return (
        df,
        bounds_summary,
        outlier_summary
    )


# -------------------------------------------------------
# Step 6 - Create clean filtered dataset
# -------------------------------------------------------

def create_filtered_dataset(df):

    # Missing values are retained because they are not
    # automatically classified as outliers.
    #
    # Only records carrying at least one Week 7 outlier
    # flag are excluded from the filtered dataset.

    filtered = (
        df.loc[
            ~df[
                "any_week7_outlier_flag"
            ]
        ]
        .copy()
    )

    return filtered


# -------------------------------------------------------
# Step 7 - Compare before and after filtering
# -------------------------------------------------------

def create_before_after_summary(
    full_df,
    filtered_df,
    dataset_name
):

    rows_before = len(full_df)
    rows_after = len(filtered_df)

    rows_removed = (
        rows_before - rows_after
    )

    percent_removed = round(
        (
            rows_removed
            /
            rows_before
        )
        * 100,
        2
    )

    comparison_rows = []

    for column in OUTLIER_FIELDS:

        median_before = (
            full_df[
                column
            ].median()
        )

        median_after = (
            filtered_df[
                column
            ].median()
        )

        comparison_rows.append({
            "Dataset":
                dataset_name,

            "Field":
                column,

            "RowsBefore":
                rows_before,

            "RowsAfter":
                rows_after,

            "RowsRemoved":
                rows_removed,

            "PercentRemoved":
                percent_removed,

            "NonNullBefore":
                int(
                    full_df[
                        column
                    ].notna().sum()
                ),

            "NonNullAfter":
                int(
                    filtered_df[
                        column
                    ].notna().sum()
                ),

            "MedianBefore":
                median_before,

            "MedianAfter":
                median_after,

            "MedianChange":
                (
                    median_after
                    -
                    median_before
                ),
        })

    return pd.DataFrame(
        comparison_rows
    )


# -------------------------------------------------------
# Step 8 - Create sample flagged records
# -------------------------------------------------------

def create_outlier_sample(
    flagged_df,
    dataset_name,
    sample_size=10
):

    preferred_columns = [
        "ListingKey",
        "CountyOrParish",
        "PropertySubType",
        "ClosePrice",
        "LivingArea",
        "DaysOnMarket",
        "price_per_sqft",
        "close_to_original_list_ratio",
        "close_price_outlier_flag",
        "living_area_outlier_flag",
        "days_on_market_outlier_flag",
        "price_per_sqft_outlier_flag",
        "close_to_original_list_ratio_outlier_flag",
        "any_week7_outlier_flag",
        "week7_outlier_field_count",
    ]

    selected_columns = [
        column
        for column in preferred_columns
        if column in flagged_df.columns
    ]

    sample = (
        flagged_df.loc[
            flagged_df[
                "any_week7_outlier_flag"
            ],
            selected_columns
        ]
        .sort_values(
            "week7_outlier_field_count",
            ascending=False
        )
        .head(sample_size)
        .copy()
    )

    sample.insert(
        0,
        "Dataset",
        dataset_name
    )

    return sample


# -------------------------------------------------------
# Step 9 - Run Week 7 pipeline
# -------------------------------------------------------

def main():

    validate_required_files()

    print(
        "Loading Week 6 datasets..."
    )

    sold = pd.read_csv(
        SOLD_INPUT,
        low_memory=False
    )

    listings = pd.read_csv(
        LISTINGS_INPUT,
        low_memory=False
    )

    require_columns(
        sold,
        "Sold"
    )

    require_columns(
        listings,
        "Listings"
    )

    sold = convert_numeric_fields(
        sold
    )

    listings = convert_numeric_fields(
        listings
    )

    print(
        f"Sold input rows: "
        f"{len(sold):,}"
    )

    print(
        f"Listings input rows: "
        f"{len(listings):,}"
    )

    print(
        "\nApplying sold outlier flags..."
    )

    (
        sold_flagged,
        sold_bounds,
        sold_outlier_summary
    ) = apply_outlier_flags(
        sold,
        "Sold"
    )

    print(
        "Applying listings outlier flags..."
    )

    (
        listings_flagged,
        listings_bounds,
        listings_outlier_summary
    ) = apply_outlier_flags(
        listings,
        "Listings"
    )

    # Full flagged datasets must preserve all rows.
    if len(sold_flagged) != len(sold):

        raise AssertionError(
            "Sold flagged dataset did not "
            "preserve row count."
        )

    if len(listings_flagged) != len(listings):

        raise AssertionError(
            "Listings flagged dataset did not "
            "preserve row count."
        )

    sold_filtered = (
        create_filtered_dataset(
            sold_flagged
        )
    )

    listings_filtered = (
        create_filtered_dataset(
            listings_flagged
        )
    )

    sold_comparison = (
        create_before_after_summary(
            sold_flagged,
            sold_filtered,
            "Sold"
        )
    )

    listings_comparison = (
        create_before_after_summary(
            listings_flagged,
            listings_filtered,
            "Listings"
        )
    )

    bounds_summary = pd.concat(
        [
            sold_bounds,
            listings_bounds
        ],
        ignore_index=True
    )

    outlier_summary = pd.concat(
        [
            sold_outlier_summary,
            listings_outlier_summary
        ],
        ignore_index=True
    )

    before_after_summary = pd.concat(
        [
            sold_comparison,
            listings_comparison
        ],
        ignore_index=True
    )

    outlier_sample = pd.concat(
        [
            create_outlier_sample(
                sold_flagged,
                "Sold"
            ),
            create_outlier_sample(
                listings_flagged,
                "Listings"
            ),
        ],
        ignore_index=True
    )

    print(
        "\nSaving Week 7 datasets..."
    )

    sold_flagged.to_csv(
        SOLD_FLAGGED_OUTPUT,
        index=False
    )

    listings_flagged.to_csv(
        LISTINGS_FLAGGED_OUTPUT,
        index=False
    )

    sold_filtered.to_csv(
        SOLD_FILTERED_OUTPUT,
        index=False
    )

    listings_filtered.to_csv(
        LISTINGS_FILTERED_OUTPUT,
        index=False
    )

    bounds_summary.to_csv(
        REPORT_DIR
        /
        "week7_iqr_bounds_summary.csv",
        index=False
    )

    outlier_summary.to_csv(
        REPORT_DIR
        /
        "week7_outlier_summary.csv",
        index=False
    )

    before_after_summary.to_csv(
        REPORT_DIR
        /
        "week7_before_after_summary.csv",
        index=False
    )

    outlier_sample.to_csv(
        REPORT_DIR
        /
        "week7_outlier_sample.csv",
        index=False
    )

    print(
        "\nWeek 7 completed."
    )

    print(
        f"Sold flagged rows: "
        f"{len(sold_flagged):,}"
    )

    print(
        f"Sold filtered rows: "
        f"{len(sold_filtered):,}"
    )

    print(
        f"Listings flagged rows: "
        f"{len(listings_flagged):,}"
    )

    print(
        f"Listings filtered rows: "
        f"{len(listings_filtered):,}"
    )

    print(
        f"Reports saved in: "
        f"{REPORT_DIR}"
    )


if __name__ == "__main__":

    main()