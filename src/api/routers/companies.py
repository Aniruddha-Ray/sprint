from fastapi import APIRouter, HTTPException

from src.api.db import read_sql, records

router = APIRouter(
    prefix="/companies",
    tags=["Companies"]
)


@router.get("/")
def companies():

    return records(read_sql("SELECT * FROM companies"))


@router.get("/{company_id}")
def company(company_id: str):
    """company_id is the NSE ticker, e.g. TCS (it was typed as int before, so every lookup failed)."""

    df = read_sql("SELECT * FROM companies WHERE id = ?", (company_id.upper(),))

    if df.empty:
        raise HTTPException(status_code=404, detail=f"Company {company_id} not found")

    return records(df)[0]
