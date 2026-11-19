from fastapi import APIRouter

from src.api.db import read_sql, records, table_columns

router = APIRouter(
    prefix="/sectors",
    tags=["Sectors"]
)


@router.get("/")
def sectors():
    """Distinct sectors.

    The raw companies sheet has no sector column, so this returns an empty
    list until sector data (companies.broad_sector) is added.
    """

    if "broad_sector" not in table_columns("companies"):
        return []

    return records(read_sql("SELECT DISTINCT broad_sector FROM companies WHERE broad_sector IS NOT NULL"))
