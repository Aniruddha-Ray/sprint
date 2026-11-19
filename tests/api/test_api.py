from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_root():

    r = client.get("/")

    assert r.status_code == 200


def test_health():

    r = client.get("/health/")

    assert r.status_code == 200


def test_companies():

    r = client.get("/companies/")

    assert r.status_code == 200

    assert len(r.json()) > 0


def test_company_by_ticker():

    r = client.get("/companies/TCS")

    assert r.status_code == 200

    assert r.json()["id"] == "TCS"


def test_company_not_found():

    assert client.get("/companies/NOTATICKER").status_code == 404


def test_screener():

    r = client.get("/screener/")

    assert r.status_code == 200

    rows = r.json()

    assert len(rows) == len({row["company_id"] for row in rows})  # latest year only


def test_sectors():

    r = client.get("/sectors/")

    assert r.status_code == 200


def test_documents_for_company():

    r = client.get("/documents/TCS")

    assert r.status_code == 200
