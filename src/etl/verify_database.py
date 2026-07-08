import sqlite3
import pandas as pd

conn = sqlite3.connect("C:\\Users\\Asus\\OneDrive\\Desktop\\Bluestock_intern\\Bluestock-sprint-1\\db\\nifty100.db")

tables = [
    "companies",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "analysis",
    "documents",
    "prosandcons"
]

for table in tables:

    rows = pd.read_sql(
        f"SELECT COUNT(*) AS count FROM {table}",
        conn
    )

    print(table, rows.iloc[0]["count"])


fk = pd.read_sql(
    "PRAGMA foreign_key_check;",
    conn
)

print(fk)


for table in tables:

    print("\n", "="*50)

    print(table.upper())

    df = pd.read_sql(
        f"SELECT * FROM {table} LIMIT 5",
        conn
    )

    print(df)


summary = []

for table in tables:

    rows = pd.read_sql(
        f"SELECT COUNT(*) AS count FROM {table}",
        conn
    ).iloc[0]["count"]

    summary.append({
        "table": table,
        "rows": rows
    })

summary = pd.DataFrame(summary)

summary.to_csv(
    "C:\\Users\\Asus\\OneDrive\\Desktop\\Bluestock_intern\\Bluestock-sprint-1\\output\\database_summary.csv",
    index=False
)

print(summary)


conn.close()