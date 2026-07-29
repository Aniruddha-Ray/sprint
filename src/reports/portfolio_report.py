import os
import sqlite3

import pandas as pd

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph


class PortfolioReport:

    def __init__(self):

        self.conn = sqlite3.connect(
            "db/nifty100.db"
        )

        os.makedirs(
            "reports/portfolio",
            exist_ok=True
        )

    def generate(self):

        companies = pd.read_sql(

            "SELECT * FROM companies",

            self.conn

        )

        ratios = pd.read_sql(

            "SELECT * FROM financial_ratios",

            self.conn

        )

        latest = ratios.groupby(

            "company_id"

        )["year"].transform("max")

        ratios = ratios[

            ratios["year"] == latest

        ]

        df = companies.merge(

            ratios,

            left_on="id",

            right_on="company_id",

            how="left"

        )

        styles = getSampleStyleSheet()

        pdf = SimpleDocTemplate(

            "reports/portfolio/portfolio_summary.pdf"

        )

        story = []

        for _, row in df.sort_values("company_name").iterrows():

            story.append(

                Paragraph(

                    f"<b>{row['company_name']}</b>",

                    styles["Heading1"]

                )

            )

            story.append(

                Paragraph(

                    f"Sector : {row['broad_sector']}",

                    styles["BodyText"]

                )

            )

            story.append(

                Paragraph(

                    f"ROE : {round(row['return_on_equity_pct'],2)}",

                    styles["BodyText"]

                )

            )

            story.append(

                Paragraph(

                    f"ROCE : {round(row['return_on_capital_employed_pct'],2)}",

                    styles["BodyText"]

                )

            )

            story.append(

                Paragraph(

                    f"NPM : {round(row['net_profit_margin_pct'],2)}",

                    styles["BodyText"]

                )

            )

            story.append(

                Paragraph(

                    f"D/E : {round(row['debt_to_equity'],2)}",

                    styles["BodyText"]

                )

            )

            story.append(

                Paragraph(

                    f"Revenue CAGR : {round(row['revenue_cagr_5yr'],2)}",

                    styles["BodyText"]

                )

            )

            story.append(

                Paragraph(

                    f"Composite Score : {round(row['composite_quality_score'],2)}",

                    styles["BodyText"]

                )

            )

            story.append(PageBreak())

        pdf.build(story)

        print("Portfolio Summary Generated")


if __name__=="__main__":

    PortfolioReport().generate()