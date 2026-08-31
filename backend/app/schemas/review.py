"""
AI Chargeback Guardian — Human Review & Approval Schemas (Step 6)

Defines data validation contracts for human-in-the-loop review actions,
state machine transitions, reviewer notes, and decision records.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator


class ReviewDecisionEnum(str, Enum):
    """Supported human reviewer decision actions."""
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    EDIT_AND_APPROVE = "EDIT_AND_APPROVE"
    NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"


class ReviewStatusEnum(str, Enum):
    """Review state lifecycle statuses."""
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EDITED_AND_APPROVED = "EDITED_AND_APPROVED"
    NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"


class HumanReviewCreateRequest(BaseModel):
    """Payload for submitting a human review decision via POST /api/v1/disputes/{id}/review."""
    decision: ReviewDecisionEnum = Field(..., description="APPROVE, REJECT, EDIT_AND_APPROVE, NEEDS_MORE_EVIDENCE")
    reviewer_reference: str = Field(default="REV-00892", description="Synthetic reviewer identifier")
    edited_response: Optional[str] = Field(default=None, description="Modified rebuttal letter (required for EDIT_AND_APPROVE)")
    reviewer_notes: Optional[str] = Field(default=None, description="Reviewer investigation notes (required for NEEDS_MORE_EVIDENCE)")

    @field_validator("edited_response")
    @classmethod
    def validate_edited_response(cls, v, info):
        decision = info.data.get("decision")
        if decision == ReviewDecisionEnum.EDIT_AND_APPROVE:
            if not v or len(v.strip()) < 10:
                raise ValueError("An edited response of at least 10 characters is required for EDIT_AND_APPROVE.")
        return v

    @field_validator("reviewer_notes")
    @classmethod
    def validate_reviewer_notes(cls, v, info):
        decision = info.data.get("decision")
        if decision == ReviewDecisionEnum.NEEDS_MORE_EVIDENCE:
            if not v or len(v.strip()) < 5:
                raise ValueError("Reviewer notes explaining what evidence is missing are required for NEEDS_MORE_EVIDENCE.")
        return v


class HumanReviewResponse(BaseModel):
    """Individual human review record."""
    id: int
    dispute_id: int
    reviewer_reference: str
    original_ai_recommendation: str
    original_ai_response: str
    reviewer_decision: str
    edited_response: Optional[str] = None
    reviewer_notes: Optional[str] = None
    reviewed_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DisputeReviewStatusResponse(BaseModel):
    """Complete review status & history payload returned by GET /api/v1/disputes/{id}/review."""
    dispute_id: int
    dispute_reference: str
    dispute_reason: str
    dispute_amount: float
    current_status: str
    original_ai_recommendation: Optional[str] = None
    original_ai_response: Optional[str] = None
    final_response: Optional[str] = None
    grounding_status: Optional[str] = None
    can_approve: bool = True
    grounding_warning: Optional[str] = None
    latest_review: Optional[HumanReviewResponse] = None
    all_reviews: List[HumanReviewResponse] = Field(default_factory=list)
