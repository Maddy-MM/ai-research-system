import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from prometheus_fastapi_instrumentator import Instrumentator

from src.config import get_settings
from src.database import init_db
from src.logging import get_logger
from api.routes_auth import router as auth_router
from api.routes_research import router as research_router

settings = get_settings()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting", extra={"app": settings.APP_NAME})
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    yield
    logger.info("Application shutting down")

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered research pipeline with JWT auth and observability",
    version="1.0.0",
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app)

app.include_router(auth_router)
app.include_router(research_router)

# Resolve frontend directory dynamically (works both locally and in Docker container)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CANDIDATE_FRONTENDS = [
    os.path.join(BASE_DIR, "..", "frontend"),
    os.path.join(BASE_DIR, "frontend"),
    os.path.abspath("frontend"),
]
FRONTEND_DIR = next((d for d in CANDIDATE_FRONTENDS if os.path.isdir(d)), os.path.join(BASE_DIR, "..", "frontend"))
TEMPLATES_DIR = os.path.join(FRONTEND_DIR, "templates")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")

if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR) if os.path.isdir(TEMPLATES_DIR) else None

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_index(request: Request):
    if templates and os.path.exists(os.path.join(TEMPLATES_DIR, "index.html")):
        return templates.TemplateResponse(request=request, name="index.html")
    return HTMLResponse("<h1>ResearchMind</h1><p>Frontend templates not found.</p>")

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}