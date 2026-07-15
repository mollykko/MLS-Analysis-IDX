import glob
import os
import re

import pandas as pd

# Week 1 – Monthly Dataset Aggregation
#
# Contents
# 1. Locate monthly listing and sold files
# 2. Confirm one file per month
# 3. Combine monthly files
# 4. Filter to Residential properties
# 5. Save combined datasets

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Data")
OUTPUT_DIR = os.path.join(BASE_DIR, "Outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def extract_month(file_path):
    """Extract YYYYMM from a CRMLS filename."""
    match = re.search(r"(20\d{4})", os.path.basename(file_path))
    return match.group(1) if match else None


def validate_monthly_files(files, dataset_name):
    """Confirm files exist and no month is included more than once."""
    if not files:
        raise FileNotFoundError(
            f"No {dataset_name} files found in {DATA_DIR}."
        )

    months = [extract_month(file_path) for file_path in files]

    duplicate_months = sorted(
        month
        for month in set(months)
        if month is not None and months.count(month) > 1
    )

    if duplicate_months:
        raise ValueError(
            f"Duplicate {dataset_name} months found: {duplicate_months}. "
            "Keep only one file for each month before rerunning."
        )


def process_dataset(file_pattern, output_name, dataset_name):
    """Combine monthly files, filter Residential records, and save the result."""

    files = sorted(
        glob.glob(
            os.path.join(DATA_DIR, file_pattern)
        )
    )

    validate_monthly_files(files, dataset_name)

    print(f"\n{dataset_name}")
    print(f"Files found: {len(files)}")

    frames = []

    for file_path in files:
        df = pd.read_csv(
            file_path,
            low_memory=False
        )

        # Some filled sold files include these helper columns.
        df = df.drop(
            columns=["latfilled", "lonfilled"],
            errors="ignore"
        )

        print(
            f"{os.path.basename(file_path)}: "
            f"{len(df):,} rows"
        )

        frames.append(df)

    combined = pd.concat(
        frames,
        ignore_index=True
    )

    rows_before_filter = len(combined)

    if "PropertyType" not in combined.columns:
        raise KeyError(
            f"PropertyType is missing from the combined {dataset_name} dataset."
        )

    residential = combined.loc[
        combined["PropertyType"] == "Residential"
    ].copy()

    rows_after_filter = len(residential)

    print(
        f"Rows after concatenation: "
        f"{rows_before_filter:,}"
    )

    print(
        f"Rows after Residential filter: "
        f"{rows_after_filter:,}"
    )

    output_path = os.path.join(
        OUTPUT_DIR,
        output_name
    )

    residential.to_csv(
        output_path,
        index=False
    )

    print(f"Saved to {output_path}")


process_dataset(
    file_pattern="CRMLSListing*.csv",
    output_name="listings.csv",
    dataset_name="Listings"
)

process_dataset(
    file_pattern="CRMLSSold*.csv",
    output_name="sold.csv",
    dataset_name="Sold"
)

print("\nWeek 1 completed.")