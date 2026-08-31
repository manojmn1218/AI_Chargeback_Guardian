"""
AI Chargeback Guardian — Health Check Endpoint
"""

from fastapi import APIRouter

from app.schemas.common import HealthResponse
from app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint for monitoring and readiness probes."""
    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version="0.1.0",
    )
