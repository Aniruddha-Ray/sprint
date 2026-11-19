# Bluestock-sprint-1

# Nifty100 Financial Data Warehouse

## Overview

ETL pipeline built using Python and SQLite for loading and validating financial data from multiple Excel files.

## Features

- Excel Loader
- Data Normalization
- Data Validation
- SQLite Database
- Load Audit Report
- Validation Report

## Tech Stack

- Python
- Pandas
- SQLite
- SQL
- OpenPyXL

## Project Structure

data/
db/
src/
tests/
output/


## Outputs

- nifty100.db
- load_audit.csv
- validation_failures.csv


You now have the required files for:

- `src/dashboard/app.py`
- `src/dashboard/utils/db.py`
- All **8 Streamlit pages**
- `src/analytics/valuation.py`
- `README.md`
- `valuation_summary.xlsx` generation
- `valuation_flags.csv` generation


# Analyst Guide

All commands run from the repository root.

## Build the database

```bash
python -m pip install -r requirements.txt
python -m src.etl.market_data        # downloads NSE sector + price files (once)
python -m src.etl.validator          # output/validation_failures.csv
python -m src.etl.load_database      # rebuilds db/nifty100.db (idempotent)
python -m src.analytics.ratio_engine # fills financial_ratios
python -m pytest tests/
```

Rows that cannot be loaded (company missing from `companies.xlsx`, `TTM`
rows, duplicate company-years) are listed in `output/rejected_rows.csv`.

Sector, peer group, market cap, P/E and P/B come from public NSE files in
`data/external/` (Nifty 500 constituents + the 28-Mar-2024 bhavcopy, i.e. FY2024
year-end prices). Sectors for symbols no longer listed by NSE are in
`data/external/sector_overrides.csv`.

## Dashboard

Run

```bash
streamlit run src/dashboard/app.py
```

## API

Run

```bash
uvicorn src.api.main:app --reload
```

## Reports

Reports are generated under

```
reports/
```

## Output Files

```
output/
```

contains

- valuation_summary.xlsx
- screener_output.xlsx
- peer_comparison.xlsx
- cashflow_intelligence.xlsx
- pros_cons_generated.csv
- company_clusters.csv