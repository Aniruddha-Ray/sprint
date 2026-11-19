from fastapi import FastAPI

from src.api.routers.companies import router as companies_router
from src.api.routers.documents import router as documents_router
from src.api.routers.health import router as health_router
from src.api.routers.peers import router as peers_router
from src.api.routers.portfolio import router as portfolio_router
from src.api.routers.screener import router as screener_router
from src.api.routers.sectors import router as sectors_router
from src.api.routers.valuation import router as valuation_router

app = FastAPI(

    title="Nifty100 Analytics API",

    version="1.0.0"

)

app.include_router(health_router)

app.include_router(companies_router)

app.include_router(screener_router)

app.include_router(sectors_router)

app.include_router(peers_router)

app.include_router(valuation_router)

app.include_router(portfolio_router)

app.include_router(documents_router)


@app.get("/")
def root():

    return {

        "message": "Nifty100 Analytics API"

    }
