from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from contextlib import asynccontextmanager

from src.config import get_settings
from src.logging import get_logger
from api.routes_auth import router as auth_router
from api.routes_research import router as research_router

settings = get_settings()
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Startup / shutdown logging
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting", extra={"app": settings.APP_NAME})
    yield
    logger.info("Application shutting down")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered research pipeline with JWT auth and observability",
    version="1.0.0",
    lifespan=lifespan,
)


# Auto-instruments all HTTP routes, exposes /metrics for Prometheus to scrape
Instrumentator().instrument(app).expose(app)


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth_router)
app.include_router(research_router)


# ---------------------------------------------------------------------------
# Health check — useful for Docker/k8s liveness probes
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}