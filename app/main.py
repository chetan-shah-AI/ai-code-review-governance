from fastapi import FastAPI

from app.api.routes.github_webhook import (
    router as github_webhook_router,
)
from app.api.routes.health import (
    router as health_router,
)
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="0.8.0",
)


app.include_router(
    health_router,
)

app.include_router(
    github_webhook_router,
)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "application": settings.app_name,
        "status": "running",
    }