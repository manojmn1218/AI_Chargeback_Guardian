"""
AI Chargeback Guardian — Auto-Pilot Rules Endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.session import get_db
from app.services.autopilot_service import AutoPilotService

router = APIRouter()


class RunAutoPilotRequest(BaseModel):
    max_batch: int = Field(default=10, ge=1, le=50)
    reviewer_id: str = Field(default="AUTOPILOT_AI_SUPERVISOR")


@router.get("/rules")
def get_autopilot_rules(db: Session = Depends(get_db)):
    """Retrieve active automated dispute SLA rules."""
    service = AutoPilotService(db)
    return {"rules": service.get_rules()}


@router.post("/run")
def run_autopilot_triage(
    payload: RunAutoPilotRequest = Body(default_factory=RunAutoPilotRequest),
    db: Session = Depends(get_db),
):
    """
    Execute 1-click automated SLA triage across pending open disputes.
    """
    try:
        service = AutoPilotService(db)
        return service.run_autopilot(max_batch=payload.max_batch, reviewer_id=payload.reviewer_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-Pilot execution failed: {str(e)}")
