"""
AI Chargeback Guardian — Evidence Intelligence Pydantic Schemas (Step 4)

Defines data validation schemas for evidence items, completeness metrics,
quality scoring, dispute-reason relevance rankings, consistency warnings,
investigation timelines, and complete combined investigation responses.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.entities import DisputeResponse, CustomerResponse, MerchantResponse, TransactionResponse
from app.schemas.ml import SHAPFactor


class EvidenceStatusEnum(str, Enum):
    """Normalized evidence status indicating presence and verification."""
    AVAILABLE_VERIFIED = "AVAILABLE_VERIFIED"
    AVAILABLE_UNVERIFIED = "AVAILABLE_UNVERIFIED"
    MISSING = "MISSING"


class EvidenceCategoryEnum(str, Enum):
    """Standardized 7 evidence categories."""
    PAYMENT = "PAYMENT"
    INVOICE = "INVOICE"
    ORDER = "ORDER"
    DELIVERY = "DELIVERY"
    REFUND = "REFUND"
    CUSTOMER_COMMUNICATION = "CUSTOMER_COMMUNICATION"
    MERCHANT_POLICY = "MERCHANT_POLICY"


class EvidenceItemDetail(BaseModel):
    """Granular evidence category item representation."""
    id: Optional[int] = None
    dispute_id: Optional[int] = None
    evidence_type: str
    category_display_name: str
    description: str
    source_reference: str
    available: bool
    verified: bool
    status: EvidenceStatusEnum
    evidence_timestamp: Optional[datetime] = None
    relevance_score: float = Field(default=0.5, description="Deterministic relevance to dispute reason (0.0 - 1.0)")
    is_strongest: bool = False
    strength_rationale: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StrongestEvidenceItem(BaseModel):
    """Top-ranked evidence item based on relevance and verification."""
    evidence_type: str
    category_display_name: str
    description: str
    source_reference: str
    status: EvidenceStatusEnum
    relevance_score: float
    rank: int
    rationale: str


class MissingEvidenceItem(BaseModel):
    """Missing evidence category with contextual investigation impact."""
    evidence_type: str
    category_display_name: str
    impact_level: str  # HIGH, MEDIUM, LOW
    impact_description: str


class EvidenceCompletenessMetrics(BaseModel):
    """Evidence completeness counts and calculated percentages."""
    expected_evidence_count: int = Field(default=7, description="Standard expected categories count")
    available_evidence_count: int = Field(..., description="Count of evidence items present (available=True)")
    verified_evidence_count: int = Field(..., description="Count of evidence items verified (available=True and verified=True)")
    missing_evidence_count: int = Field(..., description="Count of missing evidence items (expected - available)")
    availability_percentage: float = Field(..., description="available / expected * 100")
    verification_percentage: float = Field(..., description="verified / expected * 100")
    quality_score: float = Field(..., description="Weighted composite evidence quality score (0 - 100)")


class EvidenceSummaryResponse(BaseModel):
    """Structured evidence summary returned by /evidence-summary endpoint."""
    dispute_id: int
    dispute_reference: str
    dispute_reason: str
    total_expected: int = Field(default=7)
    available: int
    verified: int
    missing: int
    availability_percentage: float
    verification_percentage: float
    quality_score: float
    strongest_evidence: List[StrongestEvidenceItem] = Field(default_factory=list)
    missing_evidence: List[MissingEvidenceItem] = Field(default_factory=list)
    evidence_checklist: List[EvidenceItemDetail] = Field(default_factory=list)


class TimelineEvent(BaseModel):
    """Chronological event in the dispute investigation lifecycle."""
    event_id: str
    event_type: str  # TRANSACTION, ORDER, SHIPMENT, DELIVERY, REFUND, COMMUNICATION, DISPUTE
    title: str
    timestamp: Optional[datetime] = None
    timestamp_formatted: Optional[str] = None
    is_available: bool = True
    source: str
    description: str
    status_badge: str  # e.g., COMPLETED, PENDING, RECORDED, NOT_APPLICABLE, MISSING_TIMESTAMP


class TimelineResponse(BaseModel):
    """Investigation timeline response containing chronologically sorted events."""
    dispute_id: int
    dispute_reference: str
    events_count: int
    timeline: List[TimelineEvent] = Field(default_factory=list)


class ConsistencyWarning(BaseModel):
    """Audit warning for data anomalies or conflicting evidence records."""
    code: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    field: str
    message: str


class MLAnalysisSummary(BaseModel):
    """Integrated Step 3 ML prediction summary for the investigation view."""
    probability: float = Field(..., description="Probability of successfully contesting dispute (0.0 - 1.0)")
    score: int = Field(..., description="Normalized Case Strength Score (0 - 100)")
    classification: str = Field(..., description="WEAK, NEEDS_REVIEW, STRONG")
    recommend_contest: bool
    threshold: float
    model_version: str
    model_name: str
    top_positive_factors: List[SHAPFactor] = Field(default_factory=list)
    top_negative_factors: List[SHAPFactor] = Field(default_factory=list)
    disclaimer: str


class InvestigationDisputeInfo(DisputeResponse):
    """Dispute record enriched with associated entities."""
    customer: Optional[CustomerResponse] = None
    merchant: Optional[MerchantResponse] = None
    transaction: Optional[TransactionResponse] = None


class DisputeInvestigationResponse(BaseModel):
    """Comprehensive investigation summary response."""
    dispute: InvestigationDisputeInfo
    ml_analysis: Optional[MLAnalysisSummary] = None
    evidence_analysis: EvidenceSummaryResponse
    timeline: List[TimelineEvent] = Field(default_factory=list)
    warnings: List[ConsistencyWarning] = Field(default_factory=list)
