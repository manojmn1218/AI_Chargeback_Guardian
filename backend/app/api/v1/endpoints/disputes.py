"""
AI Chargeback Guardian — Dispute Endpoints (Step 2)
Supports listing, detailed inspection, evidence retrieval, and communications for synthetic chargebacks.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database.session import get_db
from app.services.dispute_service import DisputeService
from app.services.evidence_service import EvidenceService
from app.services.ai import AIResponseGenerator
from app.services.explainability_service import ExplainabilityService
from app.services.audit_service import AuditService
from app.services.review_service import HumanReviewService
from app.schemas import (
    DisputeResponse,
    DisputeDetailResponse,
    DisputeListResponse,
    EvidenceResponse,
    DisputeEvidenceListResponse,
    CommunicationResponse,
    DisputeInvestigationResponse,
    TimelineResponse,
    EvidenceSummaryResponse,
    AIInvestigationSummaryResponse,
    AIResponseGenerateRequest,
    DisputeExplanationResponse,
    DisputeReviewStatusResponse,
    HumanReviewCreateRequest,
    AuditTrailResponse,
)

router = APIRouter()




@router.get("", response_model=DisputeListResponse)
def list_disputes(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status (OPEN, UNDER_REVIEW, RESOLVED, CLOSED)"),
    reason: Optional[str] = Query(None, description="Filter by dispute reason"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    merchant_id: Optional[int] = Query(None, description="Filter by merchant ID"),
    db: Session = Depends(get_db),
):
    """List synthetic disputes with pagination and optional filters."""
    service = DisputeService(db)
    disputes, total = service.get_disputes(
        page=page,
        page_size=page_size,
        status=status,
        reason=reason,
        customer_id=customer_id,
        merchant_id=merchant_id,
    )

    return DisputeListResponse(
        items=[DisputeResponse.model_validate(d) for d in disputes],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{dispute_ref_or_id}", response_model=DisputeDetailResponse)
def get_dispute(dispute_ref_or_id: str, db: Session = Depends(get_db)):
    """Get full dispute details including customer, merchant, transaction, and evidence."""
    service = DisputeService(db)
    dispute = service.get_dispute_by_ref_or_id(dispute_ref_or_id)

    if not dispute:
        raise HTTPException(
            status_code=404,
            detail=f"Dispute with reference/ID '{dispute_ref_or_id}' not found",
        )

    return DisputeDetailResponse.model_validate(dispute)


@router.get("/{dispute_ref_or_id}/investigation", response_model=DisputeInvestigationResponse)
def get_dispute_investigation(dispute_ref_or_id: str, db: Session = Depends(get_db)):
    """
    Retrieve full comprehensive investigation dossier for a dispute:
    - Dispute metadata & linked entities (Customer, Merchant, Transaction)
    - Step 3 ML case strength prediction & SHAP drivers
    - Evidence completeness metrics, quality score, strongest & missing items
    - Chronological investigation timeline
    - Consistency audit warnings
    """
    service = EvidenceService(db)
    try:
        investigation = service.get_investigation(dispute_ref_or_id)
        return investigation
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate investigation summary: {str(e)}",
        )


@router.get("/{dispute_ref_or_id}/timeline", response_model=TimelineResponse)
def get_dispute_timeline(dispute_ref_or_id: str, db: Session = Depends(get_db)):
    """Retrieve chronological investigation event sequence for a dispute."""
    service = EvidenceService(db)
    try:
        return service.get_timeline_response(dispute_ref_or_id)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve timeline: {str(e)}",
        )


@router.get("/{dispute_ref_or_id}/evidence-summary", response_model=EvidenceSummaryResponse)
def get_dispute_evidence_summary(dispute_ref_or_id: str, db: Session = Depends(get_db)):
    """Retrieve evidence completeness metrics, quality score, strongest & missing evidence."""
    service = EvidenceService(db)
    try:
        return service.get_evidence_summary(dispute_ref_or_id)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve evidence summary: {str(e)}",
        )


@router.get("/{dispute_ref_or_id}/evidence", response_model=DisputeEvidenceListResponse)
def get_dispute_evidence(dispute_ref_or_id: str, db: Session = Depends(get_db)):
    """Retrieve all evidence category records attached to a specific dispute."""
    service = DisputeService(db)
    dispute, evidence_items = service.get_dispute_evidence(dispute_ref_or_id)

    if not dispute:
        raise HTTPException(
            status_code=404,
            detail=f"Dispute with reference/ID '{dispute_ref_or_id}' not found",
        )

    available_count = sum(1 for e in evidence_items if e.available)
    total_categories = len(evidence_items)
    completeness = round((available_count / total_categories * 100), 1) if total_categories > 0 else 0.0

    return DisputeEvidenceListResponse(
        dispute_reference=dispute.dispute_reference,
        items=[EvidenceResponse.model_validate(e) for e in evidence_items],
        total_available=available_count,
        total_categories=total_categories,
        completeness_percentage=completeness,
    )


@router.get("/{dispute_ref_or_id}/communications", response_model=List[CommunicationResponse])
def get_dispute_communications(dispute_ref_or_id: str, db: Session = Depends(get_db)):
    """Retrieve all communication logs attached to a specific dispute."""
    service = DisputeService(db)
    dispute, comms = service.get_dispute_communications(dispute_ref_or_id)

    if not dispute:
        raise HTTPException(
            status_code=404,
            detail=f"Dispute with reference/ID '{dispute_ref_or_id}' not found",
        )

    return [CommunicationResponse.model_validate(c) for c in comms]


@router.post("/{dispute_ref_or_id}/ai-response", response_model=AIInvestigationSummaryResponse)
def generate_dispute_ai_response(
    dispute_ref_or_id: str,
    payload: Optional[AIResponseGenerateRequest] = None,
    db: Session = Depends(get_db),
):
    """
    Generate evidence-grounded AI draft response for a dispute investigation:
    1. Compiles factual evidence dossier and Step 3 ML predictions.
    2. Constructs reason-aware prompt with strict anti-hallucination guardrails.
    3. Generates structured JSON rebuttal draft (API provider or deterministic demo fallback).
    4. Runs deterministic grounding validation checks (verifies citations & prevents unsupported claims).
    5. Calculates transparent application-level confidence score.
    6. Returns draft response for human reviewer approval (does NOT finalize/submit).
    """
    generator = AIResponseGenerator(db)
    try:
        result = generator.generate_response(dispute_ref_or_id, payload)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI Response generation failed: {str(e)}",
        )


@router.get("/{dispute_ref_or_id}/ai-response", response_model=AIInvestigationSummaryResponse)
def get_dispute_ai_response(dispute_ref_or_id: str, db: Session = Depends(get_db)):
    """Retrieve or generate evidence-grounded AI investigation response draft."""
    generator = AIResponseGenerator(db)
    try:
        return generator.generate_response(dispute_ref_or_id)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch AI response: {str(e)}",
        )


@router.get("/{dispute_ref_or_id}/explanation", response_model=DisputeExplanationResponse)
def get_dispute_explanation(dispute_ref_or_id: str, db: Session = Depends(get_db)):
    """
    Retrieve local TreeSHAP feature attributions and contributing factor explainability
    for a dispute's ML prediction.
    """
    service = ExplainabilityService(db)
    try:
        return service.get_explanation(dispute_ref_or_id)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate model explanation: {str(e)}",
        )


@router.get("/{dispute_ref_or_id}/review", response_model=DisputeReviewStatusResponse)
def get_dispute_review_status(dispute_ref_or_id: str, db: Session = Depends(get_db)):
    """
    Retrieve current human-in-the-loop review status, original AI draft, grounding validity,
    and complete review decision history.
    """
    service = HumanReviewService(db)
    try:
        return service.get_review_status(dispute_ref_or_id)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve review status: {str(e)}",
        )


@router.post("/{dispute_ref_or_id}/review", response_model=DisputeReviewStatusResponse)
def submit_dispute_review(
    dispute_ref_or_id: str,
    payload: HumanReviewCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Submit a human reviewer decision (APPROVE, REJECT, EDIT_AND_APPROVE, NEEDS_MORE_EVIDENCE):
    - ENFORCES GROUNDING SAFEGUARDS: Approval is strictly blocked if AI grounding validation FAILED.
    - Validates mandatory reviewer notes and edited responses.
    - Logs immutable audit trail events.
    """
    service = HumanReviewService(db)
    try:
        return service.submit_review(dispute_ref_or_id, payload)
    except ValueError as e:
        # Check if 404 or 422
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process review decision: {str(e)}",
        )


@router.get("/{dispute_ref_or_id}/audit", response_model=AuditTrailResponse)
def get_dispute_audit_trail(dispute_ref_or_id: str, db: Session = Depends(get_db)):
    """
    Retrieve chronological immutable audit log timeline for a dispute investigation.
    """
    service = AuditService(db)
    try:
        return service.get_audit_trail(dispute_ref_or_id)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve audit trail: {str(e)}",
        )


from pydantic import BaseModel, Field

class BatchReviewRequest(BaseModel):
    dispute_ids: List[int]
    decision: str = Field(default="APPROVE", description="APPROVE | REJECT | NEEDS_MORE_EVIDENCE")
    reviewer_reference: str = Field(default="REV-00892")
    notes: Optional[str] = "Batch triage processed via Command Deck"


@router.post("/batch-review")
def batch_review_disputes(
    request: BatchReviewRequest,
    db: Session = Depends(get_db),
):
    """
    Execute batch triage authorization across multiple selected disputes.
    """
    from app.schemas.review import ReviewDecisionEnum
    service = HumanReviewService(db)
    results = []
    
    try:
        enum_decision = ReviewDecisionEnum(request.decision)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid decision: {request.decision}")

    for dispute_id in request.dispute_ids:
        try:
            req = HumanReviewCreateRequest(
                decision=enum_decision,
                reviewer_reference=request.reviewer_reference,
                reviewer_notes=request.notes,
            )
            res = service.submit_review(str(dispute_id), req)
            results.append({"dispute_id": dispute_id, "status": "success", "decision": res.current_status})
        except Exception as e:
            results.append({"dispute_id": dispute_id, "status": "error", "error": str(e)})

    return {
        "processed_count": len(request.dispute_ids),
        "successful_count": sum(1 for r in results if r["status"] == "success"),
        "results": results,
    }




