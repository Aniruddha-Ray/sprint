import os
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

from reportlab.lib.colors import navy
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


class TearSheetGenerator:

    def __init__(self):

        self.conn = sqlite3.connect(
            "db/nifty100.db"
        )

        os.makedirs(
            "reports/tearsheets",
            exist_ok=True
        )

        os.makedirs(
            "output",
            exist_ok=True
        )

    def load(self):

        ratios = pd.read_sql(

            "SELECT * FROM financial_ratios",

            self.conn

        )

        companies = pd.read_sql(

            "SELECT * FROM companies",

            self.conn

        )

        pros = pd.read_csv(
            "output/pros_cons_generated.csv"
        )

        return ratios, companies, pros

    def revenue_chart(self, df, company):

        plt.figure(figsize=(4,2))

        plt.bar(df["year"], df["sales"])

        plt.title("Revenue")

        plt.tight_layout()

        path = f"output/{company}_rev.png"

        plt.savefig(path)

        plt.close()

        return path

    def profit_chart(self, df, company):

        plt.figure(figsize=(4,2))

        plt.bar(df["year"], df["net_profit"])

        plt.title("Net Profit")

        plt.tight_layout()

        path = f"output/{company}_profit.png"

        plt.savefig(path)

        plt.close()

        return path

    def build_pdf(self, company):

        ratios, companies, pros = self.load()

        data = ratios[
            ratios["company_id"] == company
        ]

        if len(data) < 3:
            return False

        info = companies[
            companies["id"] == company
        ].iloc[0]

        latest = data.sort_values(
            "year"
        ).iloc[-1]

        rev = self.revenue_chart(
            data,
            company
        )

        prof = self.profit_chart(
            data,
            company
        )

        pdf = canvas.Canvas(

            f"reports/tearsheets/{company}_tearsheet.pdf"

        )

        width = 595

        height = 842

        pdf.setFillColor(navy)

        pdf.rect(
            0,
            800,
            width,
            42,
            fill=1
        )

        pdf.setFillColorRGB(1,1,1)

        pdf.setFont(
            "Helvetica-Bold",
            18
        )

        pdf.drawString(

            30,

            815,

            str(info["company_name"])

        )

        pdf.setFillColorRGB(0,0,0)

        pdf.setFont(
            "Helvetica",
            11
        )

        y = 760

        metrics = [

            ("ROE", latest["return_on_equity_pct"]),

            ("ROCE", latest["return_on_capital_employed_pct"]),

            ("NPM", latest["net_profit_margin_pct"]),

            ("D/E", latest["debt_to_equity"]),

            ("Revenue CAGR", latest["revenue_cagr_5yr"]),

            ("FCF", latest["free_cash_flow_cr"])

        ]

        for name,value in metrics:

            pdf.drawString(

                30,

                y,

                f"{name}: {round(value,2)}"

            )

            y -= 18

        pdf.drawImage(

            rev,

            30,

            430,

            width=240,

            height=130

        )

        pdf.drawImage(

            prof,

            300,

            430,

            width=240,

            height=130

        )

        pdf.showPage()

        pdf.setFont(
            "Helvetica-Bold",
            15
        )

        pdf.drawString(
            30,
            800,
            "Pros"
        )

        p = pros[
            (pros.company_id==company)
            &
            (pros.type=="Pro")
        ]

        y = 770

        pdf.setFont(
            "Helvetica",
            10
        )

        for _,r in p.head(5).iterrows():

            pdf.drawString(

                40,

                y,

                "• "+str(r["text"])

            )

            y -= 18

        pdf.setFont(
            "Helvetica-Bold",
            15
        )

        pdf.drawString(
            30,
            620,
            "Cons"
        )

        c = pros[
            (pros.company_id==company)
            &
            (pros.type=="Con")
        ]

        y = 590

        pdf.setFont(
            "Helvetica",
            10
        )

        for _,r in c.head(5).iterrows():

            pdf.drawString(

                40,

                y,

                "• "+str(r["text"])

            )

            y -= 18

        pdf.save()

        return True

    def generate_all(self):

        ratios = pd.read_sql(

            "SELECT DISTINCT company_id FROM financial_ratios",

            self.conn

        )

        skipped = []

        generated = 0

        for company in ratios.company_id:

            ok = self.build_pdf(company)

            if ok:

                generated += 1

            else:

                skipped.append(
                    {"company_id":company}
                )

        pd.DataFrame(skipped).to_csv(

            "output/skipped_tearsheets.csv",

            index=False

        )

        print("="*50)
        print("Generated :",generated)
        print("Skipped   :",len(skipped))
        print("="*50)


if __name__=="__main__":

    TearSheetGenerator().generate_all()