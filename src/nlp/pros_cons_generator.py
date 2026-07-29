import sqlite3
import pandas as pd


class ProsConsGenerator:

    def __init__(self):

        self.conn = sqlite3.connect(
            "db/nifty100.db"
        )

    def generate(self):

        df = pd.read_sql(

            "SELECT * FROM financial_ratios",

            self.conn

        )

        rows = []

        latest = df.groupby(

            "company_id"

        )["year"].transform("max")

        df = df[df["year"] == latest]

        for _, row in df.iterrows():

            company = row["company_id"]

            if row["return_on_equity_pct"] > 20:

                rows.append({

                    "company_id": company,

                    "type": "Pro",

                    "rule_id": "P1",

                    "text": "High ROE",

                    "confidence_pct": 90

                })

            if row["free_cash_flow_cr"] > 0:

                rows.append({

                    "company_id": company,

                    "type": "Pro",

                    "rule_id": "P2",

                    "text": "Positive Free Cash Flow",

                    "confidence_pct": 85

                })

            if row["debt_to_equity"] == 0:

                rows.append({

                    "company_id": company,

                    "type": "Pro",

                    "rule_id": "P3",

                    "text": "Debt Free",

                    "confidence_pct": 95

                })

            if row["debt_to_equity"] > 2:

                rows.append({

                    "company_id": company,

                    "type": "Con",

                    "rule_id": "C1",

                    "text": "High Debt",

                    "confidence_pct": 90

                })

            if row["interest_coverage"] < 1.5:

                rows.append({

                    "company_id": company,

                    "type": "Con",

                    "rule_id": "C2",

                    "text": "Low Interest Coverage",

                    "confidence_pct": 90

                })

            if row["return_on_capital_employed_pct"] < 10:

                rows.append({

                    "company_id": company,

                    "type": "Con",

                    "rule_id": "C3",

                    "text": "Low ROCE",

                    "confidence_pct": 80

                })

        out = pd.DataFrame(rows)

        out.to_csv(

            "output/pros_cons_generated.csv",

            index=False

        )

        print("Pros Cons Generated")


if __name__=="__main__":

    ProsConsGenerator().generate()