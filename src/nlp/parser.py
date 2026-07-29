import re
import sqlite3
import pandas as pd


class AnalysisParser:

    def __init__(self):

        self.conn = sqlite3.connect("db/nifty100.db")

        self.pattern = re.compile(
            r"(\d+)\s*Years?:?\s*([\d.]+)%"
        )

    def parse(self):

        analysis = pd.read_sql(
            "SELECT * FROM analysis",
            self.conn
        )

        parsed = []
        failed = []

        target_columns = [

            "compounded_sales_growth",

            "compounded_profit_growth",

            "stock_price_cagr",

            "roe"

        ]

        for _, row in analysis.iterrows():

            for col in target_columns:

                text = str(row[col])

                m = self.pattern.search(text)

                if m:

                    parsed.append({

                        "company_id": row["company_id"],

                        "metric_type": col,

                        "period_years": int(m.group(1)),

                        "value_pct": float(m.group(2))

                    })

                else:

                    failed.append({

                        "company_id": row["company_id"],

                        "metric": col,

                        "text": text

                    })

        parsed_df = pd.DataFrame(parsed)

        failed_df = pd.DataFrame(failed)

        parsed_df.to_csv(

            "output/analysis_parsed.csv",

            index=False

        )

        failed_df.to_csv(

            "output/parse_failures.csv",

            index=False

        )

        print("Parser Finished")


if __name__=="__main__":

    AnalysisParser().parse()