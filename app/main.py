from fastapi import FastAPI
from app.api.routes.health import router as health_router
from app.api.routes.webhook_github import router as webhook_router

app = FastAPI(title="AI Code Review & Governance System")

app.include_router(health_router)
app.include_router(webhook_router)



