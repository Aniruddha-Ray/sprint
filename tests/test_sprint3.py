import sqlite3

import pandas as pd


conn = sqlite3.connect(
    "db/nifty100.db"
)

print("=" * 50)

print("Financial Ratios")

print(
    pd.read_sql(
        "SELECT COUNT(*) FROM financial_ratios",
        conn
    )
)

print("=" * 50)

print("Peer Percentiles")

print(
    pd.read_sql(
        "SELECT COUNT(*) FROM peer_percentiles",
        conn
    )
)

print("=" * 50)

print("Top Quality Stocks")

print(
    pd.read_sql(

        """
        SELECT company_id,
               composite_quality_score

        FROM financial_ratios

        ORDER BY composite_quality_score DESC

        LIMIT 10
        """,

        conn

    )
)

print("=" * 50)

conn.close()

print("Sprint 3 Complete.")