from fastapi import FastAPI

from app.api.games import router as games_router
from app.api.stats import router as stats_router

app = FastAPI()

app.include_router(games_router)
app.include_router(stats_router)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}