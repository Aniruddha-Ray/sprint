from fastapi import APIRouter

from src.api.db import read_sql, records, table_exists

router = APIRouter(
    prefix="/peers",
    tags=["Peers"]
)


@router.get("/")
def peers():
    """Peer percentiles. Empty until peer_percentiles is built (needs peer group data)."""

    if not table_exists("peer_percentiles"):
        return []

    return records(read_sql("SELECT * FROM peer_percentiles"))
