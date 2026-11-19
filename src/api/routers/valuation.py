import pandas as pd
from fastapi import APIRouter, HTTPException

from src.api.db import records
from src.etl.config import OUTPUT

router = APIRouter(
    prefix="/valuation",
    tags=["Valuation"]
)


@router.get("/")
def valuation():

    path = OUTPUT / "valuation_summary.xlsx"

    if not path.exists():
        raise HTTPException(status_code=404, detail="valuation_summary.xlsx not generated yet")

    return records(pd.read_excel(path))
