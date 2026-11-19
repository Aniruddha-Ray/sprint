import pandas as pd

from src.etl.config import COMPANIES_FILE
from src.etl.normaliser import normalize_columns


def load_excel(path, header=1):
    """Read a raw workbook. Row 0 is a title banner, so headers are on row 1."""

    df = pd.read_excel(path, header=header)

    df = normalize_columns(df)

    return df


if __name__ == "__main__":

    df = load_excel(COMPANIES_FILE)

    print(df.head())

    print(df.columns)
