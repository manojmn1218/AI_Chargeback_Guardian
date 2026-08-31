"""
AI Chargeback Guardian — Dispute Pydantic Schemas
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DisputeResponse(BaseModel):
    """Schema for a single dispute in API responses."""
    id: int
    dispute_id: str
    transaction_id: str
    amount: float
    currency: str = "USD"
    reason: str
    reason_code: Optional[str] = None
    status: str
    risk_level: Optional[str] = None
    risk_score: Optional[float] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    merchant_name: Optional[str] = None
    merchant_id: Optional[str] = None
    recommendation: Optional[str] = None
    transaction_date: Optional[datetime] = None
    dispute_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DisputeListResponse(BaseModel):
    """Schema for paginated dispute list."""
    disputes: list[DisputeResponse]
    total: int
    page: int = 1
    page_size: int = 20


class DisputeSummaryStats(BaseModel):
    """Dashboard summary statistics."""
    total_disputes: int = 0
    open_disputes: int = 0
    high_risk: int = 0
    medium_risk: int = 0
    low_risk: int = 0
    recommended_contests: int = 0
    human_review_cases: int = 0
