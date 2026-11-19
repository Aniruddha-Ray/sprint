import pandas as pd

from src.etl.config import BALANCE_FILE, COMPANIES_FILE, OUTPUT, PROFIT_FILE
from src.etl.loader import load_excel


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
        pd.DataFrame(
            self.failures, columns=["rule", "severity", "row", "message"]
        ).to_csv(path, index=False)

    def check_primary_key(self, df, column):

        duplicates = df[df[column].duplicated()]

        for idx in duplicates.index:
            self.add_failure(
                "DQ-01",
                "CRITICAL",
                idx,
                f"Duplicate {column} {df.at[idx, column]}"
            )

    def check_company_year(self, df):

        duplicates = df[df.duplicated(["company_id", "year"])]

        for idx in duplicates.index:
            self.add_failure(
                "DQ-02",
                "CRITICAL",
                idx,
                f"Duplicate company-year {df.at[idx, 'company_id']} {df.at[idx, 'year']}"
            )

    def check_foreign_key(self, child_df, parent_df):

        parent = set(parent_df["id"])

        for idx, value in child_df["company_id"].items():

            if value not in parent:

                self.add_failure(
                    "DQ-03",
                    "CRITICAL",
                    idx,
                    f"Invalid FK {value}"
                )

    def check_balance_sheet(self, df):
        """Total assets must equal total liabilities.

        In this dataset total_liabilities already includes equity capital and
        reserves, so equity must not be added again.
        """

        for idx, row in df.iterrows():

            assets = row["total_assets"]

            liabilities = row["total_liabilities"]

            if pd.isna(assets) or pd.isna(liabilities):
                continue

            if abs(assets - liabilities) > abs(assets) * 0.01:

                self.add_failure(
                    "DQ-04",
                    "WARNING",
                    idx,
                    "Balance sheet mismatch"
                )

    def check_positive_sales(self, df):

        for idx, value in df["sales"].items():

            if pd.notna(value) and value <= 0:

                self.add_failure(
                    "DQ-05",
                    "WARNING",
                    idx,
                    "Sales must be positive"
                )


def run_validation():

    companies_df = load_excel(COMPANIES_FILE)
    profit_df = load_excel(PROFIT_FILE)
    balance_df = load_excel(BALANCE_FILE)

    validator = DataValidator()

    validator.check_primary_key(companies_df, "id")

    validator.check_company_year(profit_df)

    validator.check_foreign_key(profit_df, companies_df)

    validator.check_balance_sheet(balance_df)

    validator.check_positive_sales(profit_df)

    OUTPUT.mkdir(exist_ok=True)

    validator.save_report(OUTPUT / "validation_failures.csv")

    return validator


if __name__ == "__main__":

    v = run_validation()

    print(f"Validation Complete: {len(v.failures)} failures")
