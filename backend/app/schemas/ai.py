"""
AI Chargeback Guardian — AI Response Engine Pydantic Schemas (Step 5)

Defines data validation schemas for structured LLM output, grounding validation results,
transparent prototype confidence scores, and end-to-end AI investigation summary responses.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.evidence import (
    EvidenceSummaryResponse,
    ConsistencyWarning,
    MLAnalysisSummary,
    InvestigationDisputeInfo,
)


class RecommendedActionEnum(str, Enum):
    """Recommended operational decision."""
    CONTEST = "CONTEST"
    REVIEW = "REVIEW"
    ACCEPT = "ACCEPT"


class GroundingStatusEnum(str, Enum):
    """Grounding validation outcome."""
    VERIFIED = "VERIFIED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    FAILED = "FAILED"


class ConfidenceLevelEnum(str, Enum):
    """Qualitative confidence bracket."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AIResponseOutput(BaseModel):
    """
    Strict structured JSON output contract expected from the LLM or fallback engine.
    """
    case_summary: str = Field(..., description="Objective case summary based solely on verified facts")
    key_verified_facts: List[str] = Field(..., description="Authoritative verified factual statements supported by database records")
    missing_information: List[str] = Field(default_factory=list, description="Explicit disclosures of missing evidence or absent records")
    conflicting_information: List[str] = Field(default_factory=list, description="Detected evidence anomalies, timestamp conflicts, or inconsistencies")
    recommended_action: str = Field(..., description="CONTEST | REVIEW | ACCEPT")
    reasoning_summary: str = Field(..., description="Operational justification directly anchored in evidence")
    draft_response: str = Field(..., description="Formal evidence-grounded draft response with traceable citations")
    evidence_references: List[str] = Field(default_factory=list, description="List of evidence references cited (e.g. [EVIDENCE: PAYMENT])")


class AIConfidenceResponse(BaseModel):
    """
    Transparent prototype confidence score and breakdown.
    Explicitly labeled as an application-level heuristic indicator, NOT an LLM probability.
    """
    confidence_score: int = Field(..., description="Prototype application confidence score (0 to 100)")
    confidence_level: ConfidenceLevelEnum = Field(..., description="HIGH (>=80), MEDIUM (50-79), LOW (<50)")
    factors: Dict[str, Any] = Field(default_factory=dict, description="Factor breakdown explaining the confidence score")
    disclaimer: str = Field(
        default="Application-level heuristic confidence indicator based on evidence completeness, verified ratio, and grounding checks; NOT an LLM probability."
    )


class GroundingValidationDetail(BaseModel):
    """
    Results of deterministic anti-hallucination and evidence-traceability validation.
    """
    is_valid: bool = Field(..., description="True if all deterministic grounding rules passed")
    status: GroundingStatusEnum = Field(..., description="VERIFIED, REVIEW_REQUIRED, or FAILED")
    passed_checks: List[str] = Field(default_factory=list)
    failed_checks: List[str] = Field(default_factory=list)
    issues: List[str] = Field(default_factory=list)
    checked_references_count: int = 0
    valid_references: List[str] = Field(default_factory=list)
    invalid_references: List[str] = Field(default_factory=list)


class AIResponseGenerateRequest(BaseModel):
    """
    Optional payload when generating or regenerating an AI draft.
    """
    force_refresh: bool = Field(default=False, description="Force re-generation instead of returning cached draft if available")
    custom_instructions: Optional[str] = Field(default=None, description="Optional reviewer guidance (treated strictly as untrusted guidance)")


class AIInvestigationSummaryResponse(BaseModel):
    """
    Comprehensive AI Response Dossier returned by POST /api/v1/disputes/{id}/ai-response.
    Integrates ML Analysis (Step 3), Evidence Analysis (Step 4), and Grounded AI Response (Step 5).
    """
    dispute_id: int
    dispute_reference: str
    dispute_reason: str
    case_summary: str
    ml_analysis: Optional[MLAnalysisSummary] = None
    evidence_summary: Optional[EvidenceSummaryResponse] = None
    key_verified_facts: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    conflicting_information: List[str] = Field(default_factory=list)
    warnings: List[ConsistencyWarning] = Field(default_factory=list)
    recommended_action: str
    reasoning_summary: str
    draft_response: str
    evidence_references: List[str] = Field(default_factory=list)
    grounding_status: GroundingStatusEnum
    grounding_details: GroundingValidationDetail
    confidence: AIConfidenceResponse
    provider: str
    model: Optional[str] = None
    is_fallback: bool = False
    generated_at: datetime = Field(default_factory=datetime.utcnow)
