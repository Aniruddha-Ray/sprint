import sqlite3

import pandas as pd

from src.etl.config import DATABASE, OUTPUT, TABLE_SOURCES

TABLES = list(TABLE_SOURCES)


def verify(db_path=DATABASE):

    conn = sqlite3.connect(db_path)

    try:
        summary = pd.DataFrame([
            {
                "table": table,
                "rows": conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0],
            }
            for table in TABLES
        ])

        fk = pd.read_sql("PRAGMA foreign_key_check;", conn)

        for table in TABLES:
            print("\n", "=" * 50)
            print(table.upper())
            print(pd.read_sql(f"SELECT * FROM {table} LIMIT 5", conn))

    finally:
        conn.close()

    OUTPUT.mkdir(exist_ok=True)

    summary.to_csv(OUTPUT / "database_summary.csv", index=False)

    print("\nForeign key violations:", len(fk))

    print(summary)

    return summary, fk


if __name__ == "__main__":
    verify()
