"""
AI Chargeback Guardian — Audit Trail Pydantic Schemas (Step 6)

Defines data contracts for chronological immutable audit logs and timeline payloads.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class AuditLogEventResponse(BaseModel):
    """Individual immutable audit event item."""
    id: int
    dispute_id: Optional[int] = None
    action: str
    actor_type: str  # SYSTEM, AI, HUMAN
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime
    timestamp_formatted: str

    model_config = ConfigDict(from_attributes=True)


class AuditTrailResponse(BaseModel):
    """Investigation audit trail payload returned by GET /api/v1/disputes/{id}/audit."""
    dispute_id: int
    dispute_reference: str
    events_count: int
    events: List[AuditLogEventResponse] = Field(default_factory=list)
