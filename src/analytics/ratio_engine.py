from __future__ import annotations

import sqlite3
import logging
from pathlib import Path
from typing import Dict

import pandas as pd

from analytics.ratios import *
from analytics.cagr import *
from analytics.cashflow_kpis import *

DATABASE_PATH = Path("db/nifty100.db")

OUTPUT_DIR = Path("output")

OUTPUT_DIR.mkdir(exist_ok=True)

EDGE_CASE_LOG = OUTPUT_DIR / "ratio_edge_cases.log"

logging.basicConfig(

    filename=EDGE_CASE_LOG,

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger(__name__)


def get_connection():
    return sqlite3.connect(DATABASE_PATH)

class DatabaseManager:

    def __init__(self, db_path=DATABASE_PATH):

        self.conn = sqlite3.connect(db_path)

    def close(self):

        self.conn.close()

    def load_tables(self):

        return {

            "companies":

            pd.read_sql(
                "SELECT * FROM companies",
                self.conn
            ),

            "profit":

            pd.read_sql(
                "SELECT * FROM profitandloss",
                self.conn
            ),

            "balance":

            pd.read_sql(
                "SELECT * FROM balancesheet",
                self.conn
            ),

            "cash":

            pd.read_sql(
                "SELECT * FROM cashflow",
                self.conn
            )

        }
    
class DataPreprocessor:

    @staticmethod
    def merge_tables(data):

        df = data["profit"]

        df = df.merge(

            data["balance"],

            on=["company_id", "year"],

            how="inner"

        )

        df = df.merge(

            data["cash"],

            on=["company_id", "year"],

            how="inner"

        )

        df = df.merge(

            data["companies"],

            left_on="company_id",

            right_on="id",

            how="left"

        )

        numeric_columns = [
            "sales",
            "operating_profit",
            "other_income",
            "interest",
            "net_profit",
            "equity_capital",
            "reserves",
            "borrowings",
            "investments",
            "total_assets",
            "operating_activity",
            "investing_activity",
            "financing_activity"
        ]

        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.sort_values(
            ["company_id", "year"]
        ).reset_index(drop=True)

        return df
    
# ---------------------------------------------------------
# Ratio Calculator
# ---------------------------------------------------------

class RatioCalculator:

    @staticmethod
    def compute_basic_ratios(df: pd.DataFrame) -> pd.DataFrame:

        records = []

        for _, row in df.iterrows():

            npm = net_profit_margin(
                row["net_profit"],
                row["sales"]
            )

            opm = operating_profit_margin(
                row["operating_profit"],
                row["sales"]
            )

            roe = return_on_equity(
                row["net_profit"],
                row["equity_capital"],
                row["reserves"]
            )

            roce = return_on_capital_employed(
                row["operating_profit"],
                row["interest"],
                row["equity_capital"],
                row["reserves"],
                row["borrowings"]
            )

            roa = return_on_assets(
                row["net_profit"],
                row["total_assets"]
            )

            debt_equity = debt_to_equity(
                row["borrowings"],
                row["equity_capital"],
                row["reserves"]
            )

            icr = interest_coverage_ratio(
                row["operating_profit"],
                row["other_income"],
                row["interest"]
            )

            turnover = asset_turnover(
                row["sales"],
                row["total_assets"]
            )

            eps = earnings_per_share(
                row["net_profit"],
                row["equity_capital"],
                row["face_value"]
            )

            bvps = book_value_per_share(
                row["equity_capital"],
                row["reserves"],
                row["face_value"]
            )

            payout = dividend_payout_ratio(
                row["dividend_payout"],
                row["net_profit"]
            )

            quality = composite_quality_score(
                roe,
                roce,
                npm,
                debt_equity,
                icr,
                turnover
            )

            records.append({

                **row.to_dict(),

                "net_profit_margin_pct": npm,

                "operating_profit_margin_pct": opm,

                "return_on_equity_pct": roe,

                "return_on_capital_employed_pct": roce,

                "return_on_assets_pct": roa,

                "debt_to_equity": debt_equity,

                "interest_coverage": icr,

                "asset_turnover": turnover,

                "earnings_per_share": eps,

                "book_value_per_share": bvps,

                "dividend_payout_ratio_pct": payout,

                "composite_quality_score": quality,

                "high_leverage_flag": int(
                    high_leverage_flag(
                        debt_equity,
                        None
                    )
                ),

                "interest_risk_flag": int(
                    interest_risk_flag(
                        icr
                    )
                )

            })

        return pd.DataFrame(records)
    
# ---------------------------------------------------------
# CAGR Calculator
# ---------------------------------------------------------

class CAGRCalculator:
        @staticmethod
        def _compute_window(series, years):

            values = []

            flags = []

            for i in range(len(series)):

                if i < years:

                    values.append(None)

                    flags.append(INSUFFICIENT)

                    continue

                start = series.iloc[i - years]

                end = series.iloc[i]

                cagr, flag = calculate_cagr(
                    start,
                    end,
                    years
                )

                values.append(cagr)

                flags.append(flag)

            return values, flags
        
        @staticmethod
        def compute(df: pd.DataFrame):

            result = []

            for company_id, group in df.groupby("company_id"):

                group = group.sort_values("year").copy()
                
                for window in [3, 5, 10]:

                    values, flags = CAGRCalculator._compute_window(
                        group["sales"],
                        window
                    )

                    group[
                        f"revenue_cagr_{window}yr"
                    ] = values

                    group[
                        f"revenue_cagr_{window}yr_flag"
                    ] = flags

                for window in [3, 5, 10]:

                    values, flags = CAGRCalculator._compute_window(
                        group["net_profit"],
                        window
                    )

                    group[
                        f"pat_cagr_{window}yr"
                    ] = values

                    group[
                        f"pat_cagr_{window}yr_flag"
                    ] = flags

                for window in [3, 5, 10]:

                    values, flags = CAGRCalculator._compute_window(
                        group["eps"],
                        window
                    )

                    group[
                        f"eps_cagr_{window}yr"
                    ] = values

                    group[
                        f"eps_cagr_{window}yr_flag"
                    ] = flags

                result.append(group)
                return pd.concat(
                        result,
                        ignore_index=True
                    )

# ---------------------------------------------------------
# Cash Flow Calculator
# ---------------------------------------------------------

class CashFlowCalculator:

    @staticmethod
    def compute(df: pd.DataFrame) -> pd.DataFrame:

        records = []

        for _, row in df.iterrows():

            # -------------------------------------------------
            # Free Cash Flow
            # -------------------------------------------------

            fcf = free_cash_flow(
                row["operating_activity"],
                row["investing_activity"]
            )

            # -------------------------------------------------
            # CFO Quality
            # -------------------------------------------------

            cfo_ratio = cfo_quality_ratio(
                row["operating_activity"],
                row["net_profit"]
            )

            cfo_label = cfo_quality_label(
                cfo_ratio
            )

            # -------------------------------------------------
            # CapEx Intensity
            # -------------------------------------------------

            capex = capex_intensity(
                row["investing_activity"],
                row["sales"]
            )

            capex_type = capex_label(
                capex
            )

            # -------------------------------------------------
            # FCF Conversion
            # -------------------------------------------------

            fcf_conv = fcf_conversion(
                fcf,
                row["operating_profit"]
            )

            # -------------------------------------------------
            # Capital Allocation Pattern
            # -------------------------------------------------

            pattern = capital_allocation_pattern(
                row["operating_activity"],
                row["investing_activity"],
                row["financing_activity"],
                cfo_ratio
            )

            # -------------------------------------------------
            # Store
            # -------------------------------------------------

            temp = row.to_dict()

            temp["free_cash_flow_cr"] = fcf

            temp["cash_from_operations_cr"] = \
                row["operating_activity"]

            temp["capex_cr"] = capex

            temp["fcf_conversion_pct"] = fcf_conv

            temp["cfo_quality_ratio"] = cfo_ratio

            temp["cfo_quality_label"] = cfo_label

            temp["capital_allocation_pattern"] = pattern

            temp["capex_category"] = capex_type

            records.append(temp)

        return pd.DataFrame(records)
    
# ---------------------------------------------------------
# SQLite Writer
# ---------------------------------------------------------

class SQLiteWriter:

    def __init__(self, conn: sqlite3.Connection):

        self.conn = conn

        self.cursor = conn.cursor()

    # -----------------------------------------------------

    def clear_table(self):

        """
        Removes previous ratio records while
        preserving schema, indexes and FK.
        """

        self.cursor.execute(
            "DELETE FROM financial_ratios"
        )

        self.conn.commit()

    # -----------------------------------------------------

    def enable_foreign_keys(self):

        self.cursor.execute(
            "PRAGMA foreign_keys = ON;"
        )

    # -----------------------------------------------------

    def save(self, df: pd.DataFrame):

        """
        Insert dataframe into financial_ratios.
        """

        self.enable_foreign_keys()

        try:

            self.clear_table()

            df.to_sql(

                "financial_ratios",

                self.conn,

                if_exists="append",

                index=False

            )

            self.conn.commit()

            logger.info(
                "financial_ratios inserted successfully."
            )

            logger.info(
                f"Rows inserted : {len(df)}"
            )

        except Exception as e:

            self.conn.rollback()

            logger.exception(e)

            raise

    # -----------------------------------------------------

    def verify(self):

        query = """
        SELECT COUNT(*)
        FROM financial_ratios
        """

        count = pd.read_sql(
            query,
            self.conn
        ).iloc[0, 0]

        logger.info(
            f"financial_ratios row count = {count}"
        )

        return count

    # -----------------------------------------------------

    def foreign_key_check(self):

        result = pd.read_sql(

            "PRAGMA foreign_key_check;",

            self.conn

        )

        if len(result) == 0:

            logger.info(
                "Foreign key check PASSED."
            )

        else:

            logger.warning(
                "Foreign key violations detected."
            )

        return result
    
# ---------------------------------------------------------
# Report Generator
# ---------------------------------------------------------

class ReportGenerator:

    def __init__(self):

        self.output_dir = OUTPUT_DIR

        self.edge_case_log = EDGE_CASE_LOG

    def generate_capital_allocation(self, df: pd.DataFrame):

            cols = [

                "company_id",

                "year",

                "capital_allocation_pattern"

            ]

            available = [

                c for c in cols

                if c in df.columns

            ]

            out = df[available].copy()

            out.to_csv(

                self.output_dir /

                "capital_allocation.csv",

                index=False

            )

            logger.info(

                "capital_allocation.csv generated."

            )
        
    def check_ratio_mismatch(

                self,

                df: pd.DataFrame

            ):

                logger.info(

                    "----- Ratio Cross Check -----"

                )

                for _, row in df.iterrows():

                    if (

                        "roe_percentage" in df.columns

                        and

                        pd.notna(row["roe_percentage"])

                        and

                        pd.notna(row["return_on_equity_pct"])

                    ):

                        diff = abs(

                            row["roe_percentage"]

                            -

                            row["return_on_equity_pct"]

                        )

                        if diff > 5:

                            logger.warning(

                                f"[ROE] "

                                f"{row['company_id']} "

                                f"{row['year']} "

                                f"Difference={diff:.2f}"

                            )

                    if (

                        "roce_percentage" in df.columns

                        and

                        pd.notna(row["roce_percentage"])

                        and

                        pd.notna(row["return_on_capital_employed_pct"])

                    ):

                        diff = abs(

                            row["roce_percentage"]

                            -

                            row["return_on_capital_employed_pct"]

                        )

                        if diff > 5:

                            logger.warning(

                                f"[ROCE] "

                                f"{row['company_id']} "

                                f"{row['year']} "

                                f"Difference={diff:.2f}"

                            )
    def check_cagr_flags(

        self,

        df: pd.DataFrame

    ):

        logger.info(

            "----- CAGR Flags -----"

        )

        flag_columns = [

            c

            for c in df.columns

            if c.endswith("_flag")

        ]

        for _, row in df.iterrows():

            for col in flag_columns:

                value = row[col]

                if (

                    pd.notna(value)

                    and

                    value != "NORMAL"

                ):

                    logger.info(

                        f"{row['company_id']} "

                        f"{row['year']} "

                        f"{col} "

                        f"{value}"

                    )
    def high_leverage_report(

            self,

            df: pd.DataFrame

        ):

            if "high_leverage_flag" not in df.columns:

                return

            risky = df[

                df["high_leverage_flag"] == 1

            ]

            logger.info(

                f"High leverage companies : "

                f"{len(risky)}"

            )
    def interest_risk_report(

        self,

        df: pd.DataFrame

    ):

        if "interest_risk_flag" not in df.columns:

            return

        risky = df[

            df["interest_risk_flag"] == 1

        ]

        logger.info(

            f"Interest risk companies : "

            f"{len(risky)}"

        )
    def missing_values_report(

        self,

        df: pd.DataFrame

    ):

        logger.info(

            "----- Missing Values -----"

        )

        missing = (

            df.isna()

            .sum()

            .sort_values(

                ascending=False

            )

        )

        for col, cnt in missing.items():

            if cnt > 0:

                logger.info(

                    f"{col}: {cnt}"

                )  
    def generate(

        self,

        df: pd.DataFrame

    ):

        self.generate_capital_allocation(df)

        self.check_ratio_mismatch(df)

        self.check_cagr_flags(df)

        self.high_leverage_report(df)

        self.interest_risk_report(df)

        self.missing_values_report(df)

        logger.info(

            "Report generation complete."

        )                      



# ---------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------

def main():

    logger.info("=" * 60)
    logger.info("Starting Financial Ratio Engine")
    logger.info("=" * 60)

    db = DatabaseManager()

    try:

        # -------------------------------------------------
        # Load Data
        # -------------------------------------------------

        logger.info("Loading database tables...")

        data = db.load_tables()

        # -------------------------------------------------
        # Merge Tables
        # -------------------------------------------------

        logger.info("Merging financial tables...")

        merged_df = DataPreprocessor.merge_tables(data)

        logger.info(
            f"Merged rows : {len(merged_df)}"
        )

        # -------------------------------------------------
        # Basic Ratios
        # -------------------------------------------------

        logger.info(
            "Computing profitability & leverage ratios..."
        )

        ratio_df = RatioCalculator.compute_basic_ratios(
            merged_df
        )

        # -------------------------------------------------
        # CAGR
        # -------------------------------------------------

        logger.info(
            "Computing CAGR metrics..."
        )

        ratio_df = CAGRCalculator.compute(
            ratio_df
        )

        # -------------------------------------------------
        # Cashflow KPIs
        # -------------------------------------------------

        logger.info(
            "Computing cashflow KPIs..."
        )

        ratio_df = CashFlowCalculator.compute(
            ratio_df
        )

        # -------------------------------------------------
        # SQLite
        # -------------------------------------------------

        logger.info(
            "Writing financial_ratios table..."
        )

        writer = SQLiteWriter(
            db.conn
        )

        writer.save(
            ratio_df
        )

        rows = writer.verify()

        writer.foreign_key_check()

        writer.vacuum()

        # -------------------------------------------------
        # Reports
        # -------------------------------------------------

        logger.info(
            "Generating reports..."
        )

        ReportGenerator().generate(
            ratio_df
        )

        logger.info("=" * 60)
        logger.info("Ratio Engine Completed Successfully")
        logger.info(f"Rows written : {rows}")
        logger.info("=" * 60)

        print()

        print("=" * 60)
        print("Financial Ratio Engine Completed")
        print(f"Rows inserted : {rows}")
        print("Database Updated Successfully")
        print("=" * 60)

    except Exception as e:

        logger.exception(e)

        print()

        print("Ratio Engine Failed.")

        print(e)

    finally:

        db.close()


if __name__ == "__main__":
    main()