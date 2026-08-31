"""
AI Chargeback Guardian — FastAPI Application Entry Point

Initializes the app, middleware, routes, and database tables.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger
from app.database.base import Base
from app.database.session import engine
from app.api.v1.router import router as api_v1_router
from app.schemas.common import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: create database tables on startup."""
    logger.info(f"Starting {settings.APP_NAME} ({settings.APP_ENV})")

    # Import all models so they register with Base.metadata
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

    yield

    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered chargeback investigation and evidence-response platform. Uses synthetic data only.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes (supports both /api/v1 and convenience alias /api)
app.include_router(api_v1_router, prefix="/api/v1")
app.include_router(api_v1_router, prefix="/api")


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Root health check (convenience, also available at /api/v1/health)
@app.get("/health", response_model=HealthResponse, tags=["Health"])
def root_health():
    """Root-level health check."""
    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version="0.1.0",
    )


# Static assets & Single Page Application (SPA) mounting for persistent unified hosting
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="frontend_assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa_frontend(full_path: str):
        """Serve built React SPA frontend for all client-side routes."""
        if full_path.startswith(("api/", "api", "docs", "openapi.json", "health")):
            return None
        file_target = FRONTEND_DIST / full_path
        if file_target.is_file():
            return FileResponse(file_target)
        return FileResponse(FRONTEND_DIST / "index.html")

