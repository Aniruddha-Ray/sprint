import re

import pandas as pd

# Raw column names that differ from db/schema.sql
COLUMN_RENAMES = {
    "other_asset": "other_assets",
}


def normalize_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace(r"[()]", "", regex=True)
    )

    return df.rename(columns=COLUMN_RENAMES)


def normalize_year(year):
    """Return the fiscal year as an int, or None.

    Handles every format present in the raw files:
    'Mar 2013', 'Dec 2012', 'Mar 2024 9m', 'Mar-13', 2013, '2013.0'.
    'TTM' (trailing twelve months) is not a fiscal year -> None.
    """

    if year is None or (not isinstance(year, str) and pd.isna(year)):
        return None

    year = str(year).strip()

    match = re.search(r"((?:19|20)\d{2})", year)

    if match:
        return int(match.group(1))

    # Two-digit form such as 'Mar-13'
    match = re.search(r"[A-Za-z]{3}[-\s']?(\d{2})$", year)

    if match:
        return 2000 + int(match.group(1))

    return None


def normalize_ticker(ticker):

    if ticker is None:
        return None

    ticker = str(ticker).upper()

    ticker = ticker.replace(".NS", "")

    ticker = ticker.replace(" EQ", "")

    ticker = ticker.strip()

    return ticker
