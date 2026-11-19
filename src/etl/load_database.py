"""Load every raw workbook into db/nifty100.db.

Run from the repository root:

    python -m src.etl.load_database

The load is idempotent: tables are recreated from db/schema.sql first, so
re-running never duplicates rows. Rows that cannot be loaded (unknown company,
unparseable year, duplicate company-year) are written to
output/rejected_rows.csv instead of aborting the whole load.
"""

import sqlite3

import pandas as pd

from src.etl import market_data
from src.etl.config import DATABASE, OUTPUT, TABLE_SOURCES, YEARLY_TABLES
from src.etl.create_db import create_database
from src.etl.loader import load_excel
from src.etl.normaliser import normalize_year


def _table_columns(conn, table):
    return [r[1] for r in conn.execute(f"PRAGMA table_info('{table}')")]


def clean_table(df, table, known_companies):
    """Return (clean_df, rejected_df) for one table."""

    rejected = []

    if table == "companies":
        dup = df["id"].duplicated()
        rejected.append(df[dup].assign(reject_reason="duplicate company id"))
        return df[~dup], pd.concat(rejected)

    orphan = ~df["company_id"].isin(known_companies)
    rejected.append(df[orphan].assign(reject_reason="company_id not in companies"))
    df = df[~orphan]

    if table in YEARLY_TABLES:
        raw_year = df["year"]
        df = df.assign(year=raw_year.map(normalize_year).astype("Int64"))

        bad_year = df["year"].isna()
        rejected.append(
            df[bad_year].assign(year=raw_year[bad_year], reject_reason="unparseable year (e.g. TTM)")
        )
        df = df[~bad_year]

        dup = df.duplicated(["company_id", "year"], keep="first")
        rejected.append(df[dup].assign(reject_reason="duplicate company-year"))
        df = df[~dup]

    return df, pd.concat(rejected)


def load_all(db_path=DATABASE):

    create_database(db_path)

    conn = sqlite3.connect(db_path)

    conn.execute("PRAGMA foreign_keys=ON")

    audit = []

    rejected_all = []

    known_companies = set()

    try:
        for table, path in TABLE_SOURCES.items():

            raw = load_excel(path)

            df, rejected = clean_table(raw, table, known_companies)

            if table == "companies":
                known_companies = set(df["id"])

            columns = [c for c in _table_columns(conn, table) if c in df.columns]

            df[columns].to_sql(table, conn, if_exists="append", index=False)

            audit.append({
                "table": table,
                "source_rows": len(raw),
                "rows_loaded": len(df),
                "rejected_rows": len(rejected),
            })

            if len(rejected):
                rejected_all.append(rejected.assign(table=table))

            print(f"{table:14} loaded {len(df):5}  rejected {len(rejected):4}")

        if market_data.SECTOR_FILE.exists() and market_data.PRICE_FILE.exists():
            print("market data   ", market_data.build(conn))
        else:
            print("market data    skipped - run `python -m src.etl.market_data` to download NSE files")

        conn.commit()

    finally:
        conn.close()

    OUTPUT.mkdir(exist_ok=True)

    pd.DataFrame(audit).to_csv(OUTPUT / "load_audit.csv", index=False)

    if rejected_all:
        pd.concat(rejected_all).reindex(columns=["table", "company_id", "year", "id", "reject_reason"]).to_csv(
            OUTPUT / "rejected_rows.csv", index=False
        )

    return pd.DataFrame(audit)


if __name__ == "__main__":

    load_all()

    print("Loading Finished")
