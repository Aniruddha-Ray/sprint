import os
import sqlite3

import pandas as pd

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.lib import colors


class SectorReport:

    def __init__(self):

        self.conn = sqlite3.connect("db/nifty100.db")

        os.makedirs(
            "reports/sector",
            exist_ok=True
        )

    def run(self):

        companies = pd.read_sql(
            "SELECT * FROM companies",
            self.conn
        )

        ratios = pd.read_sql(
            "SELECT * FROM financial_ratios",
            self.conn
        )

        df = companies.merge(
            ratios,
            left_on="id",
            right_on="company_id",
            how="left"
        )

        styles = getSampleStyleSheet()

        for sector in sorted(df["broad_sector"].dropna().unique()):

            temp = df[
                df["broad_sector"] == sector
            ]

            pdf = SimpleDocTemplate(
                f"reports/sector/{sector}_report.pdf"
            )

            elements = []

            elements.append(
                Paragraph(
                    f"<b>{sector} Sector Report</b>",
                    styles["Heading1"]
                )
            )

            median = temp[
                [
                    "return_on_equity_pct",
                    "return_on_capital_employed_pct",
                    "net_profit_margin_pct",
                    "debt_to_equity",
                    "revenue_cagr_5yr"
                ]
            ].median()

            elements.append(
                Paragraph(
                    "<b>Median KPIs</b>",
                    styles["Heading2"]
                )
            )

            for k, v in median.items():

                elements.append(
                    Paragraph(
                        f"{k}: {round(v,2)}",
                        styles["BodyText"]
                    )
                )

            data = [[

                "Company",

                "ROE",

                "ROCE",

                "NPM",

                "D/E",

                "Revenue CAGR"

            ]]

            for _, r in temp.iterrows():

                data.append([

                    str(r["company_id"]),

                    round(r["return_on_equity_pct"],2),

                    round(r["return_on_capital_employed_pct"],2),

                    round(r["net_profit_margin_pct"],2),

                    round(r["debt_to_equity"],2),

                    round(r["revenue_cagr_5yr"],2)

                ])

            table = Table(data)

            table.setStyle(TableStyle([

                ("GRID",(0,0),(-1,-1),1,colors.black),

                ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),

                ("FONTSIZE",(0,0),(-1,-1),8)

            ]))

            elements.append(table)

            pdf.build(elements)

        print("Sector Reports Generated")


if __name__=="__main__":

    SectorReport().run()