from fastapi import APIRouter

from src.api.db import read_sql, records
from src.etl.config import REPORTS

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

REPORT_FOLDERS = ["tearsheets", "sector", "portfolio"]


@router.get("/")
def documents():
    """Generated report files under reports/."""

    files = []

    for folder in REPORT_FOLDERS:

        path = REPORTS / folder

        if path.is_dir():

            for file in sorted(path.iterdir()):

                files.append({"folder": f"reports/{folder}", "file": file.name})

    return files


@router.get("/{company_id}")
def annual_reports(company_id: str):
    """Annual report links from the documents table."""

    return records(read_sql(
        "SELECT year, annual_report FROM documents WHERE company_id = ? ORDER BY year DESC",
        (company_id.upper(),),
    ))
