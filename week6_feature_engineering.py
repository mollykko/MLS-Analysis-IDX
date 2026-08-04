"""
Week 6 - Feature Engineering and Market Metrics

Required inputs:
- Outputs/sold_week5.csv
- Outputs/listings_week5.csv
- Data/SchoolDistricts/DistrictAreas2425.shp
- Data/SchoolDistricts/DistrictAreas2425.shx
- Data/SchoolDistricts/DistrictAreas2425.dbf
- Data/SchoolDistricts/DistrictAreas2425.prj
- Data/SchoolDistricts/DistrictAreas2425.cpg

Install packages:
pip install pandas numpy geopandas pyogrio shapely
"""

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd


# -------------------------------------------------------
# Step 1 - Set project folders
# -------------------------------------------------------

# This assumes the script is saved in the project root.
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "Outputs"
REPORT_DIR = BASE_DIR / "Reports"
DISTRICT_DIR = BASE_DIR / "Data" / "SchoolDistricts"

SOLD_INPUT = OUTPUT_DIR / "sold_week5.csv"
LISTINGS_INPUT = OUTPUT_DIR / "listings_week5.csv"

DISTRICT_SHP = (
    DISTRICT_DIR
    / "DistrictAreas2425.shp"
)

SOLD_OUTPUT = OUTPUT_DIR / "sold_week6.csv"
LISTINGS_OUTPUT = OUTPUT_DIR / "listings_week6.csv"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# Process school-district matches in chunks to reduce
# memory usage.
SCHOOL_JOIN_CHUNK_SIZE = 100_000


# -------------------------------------------------------
# Step 2 - Validate required files
# -------------------------------------------------------

def validate_required_files():

    required_files = [
        SOLD_INPUT,
        LISTINGS_INPUT,
        DISTRICT_DIR / "DistrictAreas2425.shp",
        DISTRICT_DIR / "DistrictAreas2425.shx",
        DISTRICT_DIR / "DistrictAreas2425.dbf",
        DISTRICT_DIR / "DistrictAreas2425.prj",
        DISTRICT_DIR / "DistrictAreas2425.cpg",
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
            f"{formatted}\n\n"
            "Keep every DistrictAreas2425 shapefile "
            "component together inside "
            "Data/SchoolDistricts/."
        )


# -------------------------------------------------------
# Step 3 - Restore data types
# -------------------------------------------------------

DATE_COLUMNS = [
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "ContractStatusChangeDate",
]

NUMERIC_COLUMNS = [
    "ClosePrice",
    "OriginalListPrice",
    "LivingArea",
    "DaysOnMarket",
    "Latitude",
    "Longitude",
]


def restore_data_types(df):

    df = df.copy()

    for column in DATE_COLUMNS:

        if column in df.columns:

            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

    for column in NUMERIC_COLUMNS:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


def require_columns(
    df,
    dataset_name,
    columns
):

    missing = [
        column
        for column in columns
        if column not in df.columns
    ]

    if missing:

        raise KeyError(
            f"{dataset_name} is missing "
            f"required columns: {missing}"
        )


# -------------------------------------------------------
# Step 4 - Engineer market metrics
# -------------------------------------------------------

REQUIRED_FEATURE_INPUTS = [
    "ClosePrice",
    "OriginalListPrice",
    "LivingArea",
    "DaysOnMarket",
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
]

ENGINEERED_COLUMNS = [
    "price_ratio",
    "close_to_original_list_ratio",
    "price_per_sqft",
    "days_on_market",
    "year",
    "month",
    "YrMo",
    "listing_to_contract_days",
    "contract_to_close_days",
]


def engineer_market_features(
    df,
    dataset_name
):

    require_columns(
        df,
        dataset_name,
        REQUIRED_FEATURE_INPUTS
    )

    df = df.copy()

    # Price Ratio
    # ClosePrice / OriginalListPrice
    valid_original_price = (
        df["OriginalListPrice"] > 0
    )

    df["price_ratio"] = np.nan

    df.loc[
        valid_original_price,
        "price_ratio"
    ] = (
        df.loc[
            valid_original_price,
            "ClosePrice"
        ]
        /
        df.loc[
            valid_original_price,
            "OriginalListPrice"
        ]
    )

    # Close-to-Original-List Ratio
    # The handbook gives this the same formula
    # as Price Ratio.
    df["close_to_original_list_ratio"] = (
        df["price_ratio"]
    )

    # Price Per Square Foot
    # ClosePrice / LivingArea
    valid_living_area = (
        df["LivingArea"] > 0
    )

    df["price_per_sqft"] = np.nan

    df.loc[
        valid_living_area,
        "price_per_sqft"
    ] = (
        df.loc[
            valid_living_area,
            "ClosePrice"
        ]
        /
        df.loc[
            valid_living_area,
            "LivingArea"
        ]
    )

    # Days on Market
    df["days_on_market"] = (
        df["DaysOnMarket"]
    )

    # Year, Month, and YrMo
    # The handbook defines these from CloseDate.
    df["year"] = (
        df["CloseDate"]
        .dt.year
        .astype("Int64")
    )

    df["month"] = (
        df["CloseDate"]
        .dt.month
        .astype("Int64")
    )

    df["YrMo"] = (
        df["CloseDate"]
        .dt.to_period("M")
        .astype("string")
    )

    df.loc[
        df["CloseDate"].isna(),
        "YrMo"
    ] = pd.NA

    # Listing-to-Contract Days
    listing_to_contract = (
        df["PurchaseContractDate"]
        -
        df["ListingContractDate"]
    ).dt.days

    # Keep invalid negative durations as missing.
    df["listing_to_contract_days"] = (
        listing_to_contract
        .where(
            listing_to_contract >= 0
        )
        .astype("Int64")
    )

    # Contract-to-Close Days
    contract_to_close = (
        df["CloseDate"]
        -
        df["PurchaseContractDate"]
    ).dt.days

    # Keep invalid negative durations as missing.
    df["contract_to_close_days"] = (
        contract_to_close
        .where(
            contract_to_close >= 0
        )
        .astype("Int64")
    )

    return df


# -------------------------------------------------------
# Step 5 - Load school-district boundaries
# -------------------------------------------------------

DISTRICT_OUTPUT_COLUMNS = [
    "elementary_district_name",
    "elementary_district_code",
    "secondary_district_name",
    "secondary_district_code",
    "unified_district_name",
    "unified_district_code",
]


def find_district_column(
    columns,
    candidates,
    description
):

    for candidate in candidates:

        if candidate in columns:

            return candidate

    raise KeyError(
        f"Could not find the {description} column "
        "in the school-district shapefile. "
        f"Available columns: {list(columns)}"
    )


def load_school_district_boundaries():

    districts = gpd.read_file(
        DISTRICT_SHP
    )

    if districts.crs is None:

        raise ValueError(
            "The district shapefile does not have "
            "a coordinate reference system. "
            "Confirm that DistrictAreas2425.prj "
            "is in the same folder."
        )

    # Shapefiles may truncate field names.
    name_column = find_district_column(
        districts.columns,
        [
            "DistrictName",
            "DistrictNa"
        ],
        "district name"
    )

    type_column = find_district_column(
        districts.columns,
        [
            "DistrictType",
            "DistrictTy"
        ],
        "district type"
    )

    code_column = find_district_column(
        districts.columns,
        [
            "CDCode",
            "CDSCode",
            "FedID"
        ],
        "district code"
    )

    districts = districts[
        [
            name_column,
            type_column,
            code_column,
            "geometry"
        ]
    ].rename(
        columns={
            name_column: "district_name",
            type_column: "district_type",
            code_column: "district_code",
        }
    )

    districts["district_name"] = (
        districts["district_name"]
        .astype("string")
    )

    districts["district_code"] = (
        districts["district_code"]
        .astype("string")
    )

    districts["district_type"] = (
        districts["district_type"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    # Normalize district-type names.
    type_map = {
        "elementary": "elementary",
        "high": "secondary",
        "secondary": "secondary",
        "unified": "unified",
    }

    districts["district_type"] = (
        districts["district_type"]
        .map(type_map)
    )

    # Remove unsupported district types.
    districts = districts.loc[
        districts["district_type"].notna()
    ].copy()

    # Remove missing or empty geometries.
    districts = districts.loc[
        districts.geometry.notna()
        &
        ~districts.geometry.is_empty
    ].copy()

    print(
        "\nSchool-district shapefile loaded."
    )

    print(
        f"District polygons: "
        f"{len(districts):,}"
    )

    print(
        f"District CRS: "
        f"{districts.crs}"
    )

    print(
        "\nDistrict types:"
    )

    print(
        districts[
            "district_type"
        ].value_counts(
            dropna=False
        )
    )

    return districts


# -------------------------------------------------------
# Step 6 - Identify usable property coordinates
# -------------------------------------------------------

def convert_flag_to_boolean(series):

    return (
        series
        .astype("string")
        .str.strip()
        .str.lower()
        .map({
            "true": True,
            "false": False,
            "1": True,
            "0": False,
        })
        .fillna(False)
        .astype(bool)
    )


def usable_coordinate_mask(df):

    require_columns(
        df,
        "Geographic enrichment dataset",
        [
            "Latitude",
            "Longitude"
        ]
    )

    mask = (
        df["Latitude"].notna()
        &
        df["Longitude"].notna()
        &
        df["Latitude"].between(
            32,
            42.1,
            inclusive="both"
        )
        &
        df["Longitude"].between(
            -124.5,
            -114,
            inclusive="both"
        )
    )

    # Use the Week 5 geographic-quality flag.
    if (
        "any_geographic_issue_flag"
        in df.columns
    ):

        geographic_issue = (
            convert_flag_to_boolean(
                df[
                    "any_geographic_issue_flag"
                ]
            )
        )

        mask &= ~geographic_issue

    return mask


# -------------------------------------------------------
# Step 7 - Match one coordinate chunk to school districts
# -------------------------------------------------------

def join_school_district_chunk(
    chunk,
    districts
):

    # MLS longitude and latitude values are WGS84.
    property_points = (
        gpd.GeoDataFrame(
            chunk[
                ["property_row_id"]
            ].copy(),
            geometry=gpd.points_from_xy(
                chunk["Longitude"],
                chunk["Latitude"]
            ),
            crs="EPSG:4326"
        )
    )

    # Transform property points into the same CRS
    # used by the school-district polygons.
    property_points = (
        property_points.to_crs(
            districts.crs
        )
    )

    matches = gpd.sjoin(
        property_points,
        districts,
        how="left",
        predicate="within"
    )

    # Remove properties without a district match.
    matches = matches.loc[
        matches[
            "district_type"
        ].notna()
    ].copy()

    if matches.empty:

        return pd.DataFrame(
            index=chunk[
                "property_row_id"
            ]
        )

    # One property can correctly match:
    # - one Unified district, or
    # - one Elementary and one Secondary district.
    #
    # If multiple polygons of the same district type
    # match a point, retain one deterministic match.
    matches = (
        matches
        .sort_values(
            [
                "property_row_id",
                "district_type",
                "district_code",
                "district_name"
            ],
            na_position="last"
        )
        .drop_duplicates(
            subset=[
                "property_row_id",
                "district_type"
            ],
            keep="first"
        )
    )

    district_names = (
        matches.pivot(
            index="property_row_id",
            columns="district_type",
            values="district_name"
        )
        .rename(
            columns={
                "elementary":
                    "elementary_district_name",
                "secondary":
                    "secondary_district_name",
                "unified":
                    "unified_district_name",
            }
        )
    )

    district_codes = (
        matches.pivot(
            index="property_row_id",
            columns="district_type",
            values="district_code"
        )
        .rename(
            columns={
                "elementary":
                    "elementary_district_code",
                "secondary":
                    "secondary_district_code",
                "unified":
                    "unified_district_code",
            }
        )
    )

    return district_names.join(
        district_codes,
        how="outer"
    )


# -------------------------------------------------------
# Step 8 - Add districts without duplicating MLS rows
# -------------------------------------------------------

def add_school_districts(
    df,
    districts,
    dataset_name
):

    df = df.copy()

    original_row_count = len(df)

    # Create a temporary unique row identifier.
    df["property_row_id"] = np.arange(
        original_row_count,
        dtype="int64"
    )

    # Initialize district columns.
    for column in DISTRICT_OUTPUT_COLUMNS:

        df[column] = pd.Series(
            pd.NA,
            index=df.index,
            dtype="string"
        )

    eligible_mask = (
        usable_coordinate_mask(df)
    )

    eligible_properties = df.loc[
        eligible_mask,
        [
            "property_row_id",
            "Latitude",
            "Longitude"
        ]
    ].copy()

    district_match_parts = []

    for start in range(
        0,
        len(eligible_properties),
        SCHOOL_JOIN_CHUNK_SIZE
    ):

        stop = (
            start
            +
            SCHOOL_JOIN_CHUNK_SIZE
        )

        coordinate_chunk = (
            eligible_properties
            .iloc[start:stop]
            .copy()
        )

        chunk_matches = (
            join_school_district_chunk(
                coordinate_chunk,
                districts
            )
        )

        district_match_parts.append(
            chunk_matches
        )

        print(
            f"{dataset_name}: processed "
            f"{min(stop, len(eligible_properties)):,} "
            f"of {len(eligible_properties):,} "
            "eligible coordinates"
        )

    if district_match_parts:

        district_matches = pd.concat(
            district_match_parts,
            axis=0
        )

        district_matches = (
            district_matches.loc[
                ~district_matches.index.duplicated(
                    keep="first"
                )
            ]
        )

        for column in DISTRICT_OUTPUT_COLUMNS:

            if column in district_matches.columns:

                match_map = (
                    district_matches[column]
                )

                df[column] = (
                    df["property_row_id"]
                    .map(match_map)
                    .astype("string")
                )

    district_name_columns = [
        "elementary_district_name",
        "secondary_district_name",
        "unified_district_name",
    ]

    df["school_district_match_flag"] = (
        df[
            district_name_columns
        ]
        .notna()
        .any(axis=1)
    )

    # Confirm the spatial join did not duplicate rows.
    if len(df) != original_row_count:

        raise AssertionError(
            f"{dataset_name} row count changed "
            "during the school-district join."
        )

    school_match_summary = {
        "Dataset": dataset_name,

        "TotalRows":
            original_row_count,

        "EligibleCoordinateRows":
            int(
                eligible_mask.sum()
            ),

        "IneligibleCoordinateRows":
            int(
                (~eligible_mask).sum()
            ),

        "MatchedRows":
            int(
                df[
                    "school_district_match_flag"
                ].sum()
            ),

        "UnmatchedEligibleRows":
            int(
                (
                    eligible_mask
                    &
                    ~df[
                        "school_district_match_flag"
                    ]
                ).sum()
            ),

        "ElementaryMatches":
            int(
                df[
                    "elementary_district_name"
                ].notna().sum()
            ),

        "SecondaryMatches":
            int(
                df[
                    "secondary_district_name"
                ].notna().sum()
            ),

        "UnifiedMatches":
            int(
                df[
                    "unified_district_name"
                ].notna().sum()
            ),
    }

    # Remove the temporary identifier.
    df = df.drop(
        columns="property_row_id"
    )

    return (
        df,
        school_match_summary
    )


# -------------------------------------------------------
# Step 9 - Validate engineered features
# -------------------------------------------------------

def feature_validation_summary(
    df,
    dataset_name
):

    validation_rows = []

    for column in ENGINEERED_COLUMNS:

        series = df[column]

        if pd.api.types.is_numeric_dtype(
            series
        ):

            numeric_series = (
                pd.to_numeric(
                    series,
                    errors="coerce"
                )
                .astype("float64")
            )

            infinite_count = int(
                np.isinf(
                    numeric_series
                ).sum()
            )

        else:

            infinite_count = 0

        validation_rows.append({
            "Dataset":
                dataset_name,

            "Feature":
                column,

            "TotalRows":
                len(df),

            "NonNullCount":
                int(
                    series.notna().sum()
                ),

            "MissingCount":
                int(
                    series.isna().sum()
                ),

            "InfiniteCount":
                infinite_count,
        })

    return pd.DataFrame(
        validation_rows
    )


# -------------------------------------------------------
# Step 10 - Create segmented county summary
# -------------------------------------------------------

def create_county_summary(sold):

    required_columns = [
        "CountyOrParish",
        "ClosePrice",
        "OriginalListPrice",
    ] + ENGINEERED_COLUMNS

    require_columns(
        sold,
        "Sold",
        required_columns
    )

    county_summary = (
        sold
        .groupby(
            "CountyOrParish",
            dropna=False
        )
        .agg(
            transaction_count=(
                "ClosePrice",
                "count"
            ),

            median_close_price=(
                "ClosePrice",
                "median"
            ),

            median_original_list_price=(
                "OriginalListPrice",
                "median"
            ),

            median_price_ratio=(
                "price_ratio",
                "median"
            ),

            median_price_per_sqft=(
                "price_per_sqft",
                "median"
            ),

            median_days_on_market=(
                "days_on_market",
                "median"
            ),

            median_listing_to_contract_days=(
                "listing_to_contract_days",
                "median"
            ),

            median_contract_to_close_days=(
                "contract_to_close_days",
                "median"
            ),
        )
        .reset_index()
        .sort_values(
            "transaction_count",
            ascending=False
        )
    )

    return county_summary


# -------------------------------------------------------
# Step 11 - Create sample engineered output
# -------------------------------------------------------

def create_sample_output(sold):

    identifier_columns = [
        "ListingKey",
        "CountyOrParish",
        "PropertySubType",
        "CloseDate",
        "ClosePrice",
        "OriginalListPrice",
        "LivingArea",
        "DaysOnMarket",
        "PurchaseContractDate",
        "ListingContractDate",
    ]

    school_columns = (
        DISTRICT_OUTPUT_COLUMNS
        +
        [
            "school_district_match_flag"
        ]
    )

    selected_columns = [
        column
        for column in (
            identifier_columns
            +
            ENGINEERED_COLUMNS
            +
            school_columns
        )
        if column in sold.columns
    ]

    complete_metrics_mask = (
    sold[
        ENGINEERED_COLUMNS
    ]
    .notna()
    .all(axis=1)
    &
    sold[
        "school_district_match_flag"
    ]
    )

    sample = (
        sold.loc[
            complete_metrics_mask,
            selected_columns
        ]
        .head(10)
    )

    # If there are fewer than 10 completely populated
    # records, fill the remainder with other records.
    if len(sample) < 10:

        remaining = sold.loc[
            ~sold.index.isin(
                sample.index
            ),
            selected_columns
        ]

        sample = pd.concat(
            [
                sample,
                remaining.head(
                    10 - len(sample)
                )
            ]
        )

    return sample


# -------------------------------------------------------
# Step 12 - Run the complete Week 6 pipeline
# -------------------------------------------------------

def main():

    validate_required_files()

    print(
        "Loading Week 5 datasets..."
    )

    sold = pd.read_csv(
        SOLD_INPUT,
        low_memory=False
    )

    listings = pd.read_csv(
        LISTINGS_INPUT,
        low_memory=False
    )

    input_row_counts = {
        "Sold": len(sold),
        "Listings": len(listings),
    }

    print(
        f"Sold input rows: "
        f"{len(sold):,}"
    )

    print(
        f"Listings input rows: "
        f"{len(listings):,}"
    )

    print(
        "\nRestoring data types..."
    )

    sold = restore_data_types(
        sold
    )

    listings = restore_data_types(
        listings
    )

    print(
        "\nEngineering market metrics..."
    )

    sold = engineer_market_features(
        sold,
        "Sold"
    )

    listings = engineer_market_features(
        listings,
        "Listings"
    )

    print(
        "\nLoading school-district boundaries..."
    )

    districts = (
        load_school_district_boundaries()
    )

    print(
        "\nMatching sold properties "
        "to school districts..."
    )

    (
        sold,
        sold_school_summary
    ) = add_school_districts(
        sold,
        districts,
        "Sold"
    )

    print(
        "\nMatching listing properties "
        "to school districts..."
    )

    (
        listings,
        listings_school_summary
    ) = add_school_districts(
        listings,
        districts,
        "Listings"
    )

    # Confirm that Week 6 preserved all rows.
    if (
        len(sold)
        !=
        input_row_counts["Sold"]
    ):

        raise AssertionError(
            "Sold row count changed "
            "during Week 6."
        )

    if (
        len(listings)
        !=
        input_row_counts["Listings"]
    ):

        raise AssertionError(
            "Listings row count changed "
            "during Week 6."
        )

    print(
        "\nCreating validation reports..."
    )

    feature_validation = pd.concat(
        [
            feature_validation_summary(
                sold,
                "Sold"
            ),

            feature_validation_summary(
                listings,
                "Listings"
            ),
        ],
        ignore_index=True
    )

    school_match_summary = pd.DataFrame(
        [
            sold_school_summary,
            listings_school_summary
        ]
    )

    county_summary = (
        create_county_summary(
            sold
        )
    )

    sample_output = (
        create_sample_output(
            sold
        )
    )

    feature_validation.to_csv(
        REPORT_DIR
        /
        "week6_feature_validation_summary.csv",
        index=False
    )

    school_match_summary.to_csv(
        REPORT_DIR
        /
        "week6_school_district_match_summary.csv",
        index=False
    )

    county_summary.to_csv(
        REPORT_DIR
        /
        "week6_county_market_summary.csv",
        index=False
    )

    sample_output.to_csv(
        REPORT_DIR
        /
        "week6_sample_engineered_metrics.csv",
        index=False
    )

    print(
        "\nSaving Week 6 datasets..."
    )

    sold.to_csv(
        SOLD_OUTPUT,
        index=False
    )

    listings.to_csv(
        LISTINGS_OUTPUT,
        index=False
    )

    print(
        "\nWeek 6 completed."
    )

    print(
        f"Sold rows preserved: "
        f"{len(sold):,}"
    )

    print(
        f"Listings rows preserved: "
        f"{len(listings):,}"
    )

    print(
        f"Saved: {SOLD_OUTPUT}"
    )

    print(
        f"Saved: {LISTINGS_OUTPUT}"
    )

    print(
        f"Reports saved in: "
        f"{REPORT_DIR}"
    )


if __name__ == "__main__":

    main()