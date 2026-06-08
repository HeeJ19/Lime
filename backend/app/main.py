from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from app.routers import health, items, recommendations  # noqa: E402 — must load env before importing routers/services

app = FastAPI(title="Lime AI Service")

app.include_router(health.router)
app.include_router(items.router)
app.include_router(recommendations.router)
