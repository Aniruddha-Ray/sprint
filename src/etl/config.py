"""Single source of truth for project paths.

Every path is resolved from the repository root, so scripts work no matter
which directory they are launched from (and SQLite never silently creates a
new, empty database somewhere else).
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA = PROJECT_ROOT / "data" / "raw"

OUTPUT = PROJECT_ROOT / "output"

REPORTS = PROJECT_ROOT / "reports"

DATABASE = PROJECT_ROOT / "db" / "nifty100.db"

SCHEMA = PROJECT_ROOT / "db" / "schema.sql"

SCREENER_CONFIG = PROJECT_ROOT / "config" / "screener_config.yaml"

COMPANIES_FILE = RAW_DATA / "companies.xlsx"

PROFIT_FILE = RAW_DATA / "profitandloss.xlsx"

BALANCE_FILE = RAW_DATA / "balancesheet.xlsx"

CASHFLOW_FILE = RAW_DATA / "cashflow.xlsx"

ANALYSIS_FILE = RAW_DATA / "analysis.xlsx"

DOCUMENTS_FILE = RAW_DATA / "documents.xlsx"

PROSCONS_FILE = RAW_DATA / "prosandcons.xlsx"

# table name -> source file, in FK-safe load order (parents first)
TABLE_SOURCES = {
    "companies": COMPANIES_FILE,
    "profitandloss": PROFIT_FILE,
    "balancesheet": BALANCE_FILE,
    "cashflow": CASHFLOW_FILE,
    "analysis": ANALYSIS_FILE,
    "documents": DOCUMENTS_FILE,
    "prosandcons": PROSCONS_FILE,
}

# tables keyed by (company_id, year)
YEARLY_TABLES = {"profitandloss", "balancesheet", "cashflow", "documents"}
