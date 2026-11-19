"""Shared database helpers for the API routers."""

import sqlite3

import pandas as pd
from fastapi import HTTPException

from src.etl.config import DATABASE


def records(df: pd.DataFrame) -> list[dict]:
    """DataFrame -> JSON-safe records (NaN/NaT become null)."""

    return df.astype(object).where(df.notna(), None).to_dict(orient="records")


def read_sql(sql: str, params=()) -> pd.DataFrame:

    if not DATABASE.exists():
        raise HTTPException(status_code=503, detail=f"Database not found at {DATABASE}. Run the ETL first.")

    conn = sqlite3.connect(DATABASE)

    try:
        return pd.read_sql(sql, conn, params=params)
    finally:
        conn.close()


def table_exists(name: str) -> bool:

    df = read_sql("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))

    return len(df) > 0


def table_columns(name: str) -> list[str]:

    return read_sql(f"PRAGMA table_info('{name}')")["name"].tolist()
