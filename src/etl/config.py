from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA = PROJECT_ROOT / "data" / "raw"

OUTPUT = PROJECT_ROOT / "output"

DATABASE = PROJECT_ROOT / "db" / "nifty100.db"

COMPANIES_FILE = RAW_DATA / "companies.xlsx"

PROFIT_FILE = RAW_DATA / "profitandloss.xlsx"

BALANCE_FILE = RAW_DATA / "balancesheet.xlsx"