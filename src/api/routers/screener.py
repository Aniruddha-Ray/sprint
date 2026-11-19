from fastapi import APIRouter, HTTPException

from src.api.db import read_sql, records, table_exists

router = APIRouter(
    prefix="/screener",
    tags=["Screener"]
)


@router.get("/")
def screener(latest_only: bool = True):
    """Rows from financial_ratios (latest year per company by default)."""

    if not table_exists("financial_ratios"):
        raise HTTPException(status_code=503, detail="financial_ratios not built. Run the ratio engine.")

    sql = "SELECT * FROM financial_ratios"

    if latest_only:
        sql += """
        WHERE year = (SELECT MAX(year) FROM financial_ratios f2
                      WHERE f2.company_id = financial_ratios.company_id)
        """

    return records(read_sql(sql))
