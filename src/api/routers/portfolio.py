import pandas as pd
from fastapi import APIRouter, HTTPException

from src.api.db import records
from src.etl.config import OUTPUT

router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"]
)


@router.get("/")
def portfolio():

    path = OUTPUT / "company_clusters.csv"

    if not path.exists():
        raise HTTPException(status_code=404, detail="company_clusters.csv not generated yet. Run clustering.")

    return records(pd.read_csv(path))
