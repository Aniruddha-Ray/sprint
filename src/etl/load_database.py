import sqlite3
import pandas as pd

from loader import load_excel

conn = sqlite3.connect("C:\\Users\\Asus\\OneDrive\\Desktop\\Bluestock_intern\\Bluestock-sprint-1\\db\\nifty100.db")

conn.execute("PRAGMA foreign_keys=ON")

audit = []

def load_table(file_path, table_name):

    df = load_excel(file_path)

    df.to_sql(
        table_name,
        conn,
        if_exists="append",
        index=False
    )

    audit.append({
        "table": table_name,
        "rows_loaded": len(df),
        "rejected_rows": 0
    })

    print(f"{table_name} Loaded ({len(df)} rows)")

load_table("C:\\Users\\Asus\\OneDrive\\Desktop\\Bluestock_intern\\Bluestock-sprint-1\\data\\raw\\companies.xlsx","companies")

load_table("C:\\Users\\Asus\\OneDrive\\Desktop\\Bluestock_intern\\Bluestock-sprint-1\\data\\raw\\profitandloss.xlsx","profitandloss")

load_table("C:\\Users\\Asus\\OneDrive\\Desktop\\Bluestock_intern\\Bluestock-sprint-1\\data\\raw\\balancesheet.xlsx","balancesheet")

load_table("C:\\Users\\Asus\\OneDrive\\Desktop\\Bluestock_intern\\Bluestock-sprint-1\\data\\raw\\cashflow.xlsx","cashflow")

load_table("C:\\Users\\Asus\\OneDrive\\Desktop\\Bluestock_intern\\Bluestock-sprint-1\\data\\raw\\analysis.xlsx","analysis")

load_table("C:\\Users\\Asus\\OneDrive\\Desktop\\Bluestock_intern\\Bluestock-sprint-1\\data\\raw\\documents.xlsx","documents")

load_table("C:\\Users\\Asus\\OneDrive\\Desktop\\Bluestock_intern\\Bluestock-sprint-1\\data\\raw\\prosandcons.xlsx","prosandcons")



pd.DataFrame(audit).to_csv(
    "C:\\Users\\Asus\\OneDrive\\Desktop\\Bluestock_intern\\Bluestock-sprint-1\\output\\load_audit.csv",
    index=False
)

conn.commit()

conn.close()

print("Loading Finished")

