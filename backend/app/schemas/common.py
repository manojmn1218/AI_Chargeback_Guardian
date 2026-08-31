"""
AI Chargeback Guardian — Common Pydantic Schemas
"""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    app_name: str
    version: str


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: str | None = None
