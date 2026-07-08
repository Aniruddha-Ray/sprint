import pandas as pd

class DataValidator:

    def __init__(self):
        self.failures = []

    def add_failure(self, rule, severity, row, message):
        self.failures.append({
            "rule": rule,
            "severity": severity,
            "row": row,
            "message": message
        })

    def save_report(self, path):
        pd.DataFrame(self.failures).to_csv(path, index=False)

    
    def check_primary_key(self, df, column):

        duplicates = df[df[column].duplicated()]

        for idx in duplicates.index:
            self.add_failure(
                "DQ-01",
                "CRITICAL",
                idx,
                f"Duplicate {column}"
            )

    def check_company_year(self, df):

        duplicates = df[df.duplicated(["id", "year"])]

        for idx in duplicates.index:
            self.add_failure(
                "DQ-02",
                "CRITICAL",
                idx,
                "Duplicate company-year"
            )

    def check_foreign_key(self, child_df, parent_df):

        parent = set(parent_df["id"])

        for idx, value in enumerate(child_df["id"]):

            if value not in parent:

                self.add_failure(
                    "DQ-03",
                    "CRITICAL",
                    idx,
                    f"Invalid FK {value}"
                )

    def check_balance_sheet(self, df):

        for idx, row in df.iterrows():

            assets = row["total_assets"]

            liabilities = row["total_liabilities"]

            equity = row["equity_capital"]

            if pd.isna(assets) or pd.isna(liabilities) or pd.isna(equity):
                continue

            if abs(assets - (liabilities + equity)) > assets * 0.01:

                self.add_failure(
                    "DQ-04",
                    "WARNING",
                    idx,
                    "Balance sheet mismatch"
                )

    def check_positive_sales(self, df):

        for idx, value in enumerate(df["sales"]):

            if pd.notna(value) and value <= 0:

                self.add_failure(
                    "DQ-05",
                    "WARNING",
                    idx,
                    "Sales must be positive"
                )


from loader import load_excel
from config import (
    COMPANIES_FILE,
    PROFIT_FILE,
    BALANCE_FILE
)

companies_df = load_excel(COMPANIES_FILE, header =1)
profit_df = load_excel(PROFIT_FILE, header =1)
balance_df = load_excel(BALANCE_FILE, header =1)

print("Companies_df:\n", companies_df.head())
print("Profit_df:\n", profit_df.head())
print("Balance_df:\n", balance_df.head())

validator = DataValidator()

validator.check_primary_key(companies_df, "id")

validator.check_company_year(profit_df)

validator.check_foreign_key(
    profit_df,
    companies_df
)

validator.check_balance_sheet(balance_df)

validator.check_positive_sales(profit_df)

validator.save_report(
    "C:\\Users\\Asus\\OneDrive\\Desktop\\Bluestock_intern\\Bluestock-sprint-1\\output\\validation_failures.csv"
)

print("Validation Complete")