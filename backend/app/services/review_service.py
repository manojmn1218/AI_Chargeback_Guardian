"""
AI Chargeback Guardian — Human Review & Approval Service (Step 6)

Implements the Human-in-the-Loop decision layer:
1. Validates reviewer decision state transitions (APPROVE, REJECT, EDIT_AND_APPROVE, NEEDS_MORE_EVIDENCE).
2. ENFORCES GROUNDING SAFEGUARDS: Strictly prohibits APPROVE or EDIT_AND_APPROVE if grounding validation FAILED.
3. Records human review entries and updates dispute resolution status.
4. Emits immutable audit log events for every reviewer action.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.models import Dispute, HumanReview
from app.schemas.review import (
    ReviewDecisionEnum,
    ReviewStatusEnum,
    HumanReviewCreateRequest,
    HumanReviewResponse,
    DisputeReviewStatusResponse,
)
from app.services.ai.response_generator import AIResponseGenerator
from app.services.audit_service import AuditService
from app.schemas.ai import GroundingStatusEnum


class HumanReviewService:
    """Service layer for human review workflows and decision enforcement."""

    def __init__(self, db: Session):
        self.db = db
        self.ai_generator = AIResponseGenerator(db)
        self.audit_service = AuditService(db)

    def get_review_status(self, dispute_ref_or_id: str) -> DisputeReviewStatusResponse:
        """
        Get current review status, AI draft, grounding validity, and review history.
        """
        if str(dispute_ref_or_id).isdigit():
            dispute = self.db.query(Dispute).filter(Dispute.id == int(dispute_ref_or_id)).first()
        else:
            dispute = self.db.query(Dispute).filter(Dispute.dispute_reference == str(dispute_ref_or_id)).first()

        if not dispute:
            raise ValueError(f"Dispute '{dispute_ref_or_id}' not found.")

        # Get AI Response & Grounding Status
        ai_resp = self.ai_generator.generate_response(str(dispute.id))
        is_grounding_failed = ai_resp.grounding_status == GroundingStatusEnum.FAILED

        # Query reviews
        reviews = (
            self.db.query(HumanReview)
            .filter(HumanReview.dispute_id == dispute.id)
            .order_by(HumanReview.reviewed_at.desc())
            .all()
        )

        latest_review = reviews[0] if reviews else None
        current_status = latest_review.reviewer_decision if latest_review else ReviewStatusEnum.PENDING_REVIEW.value

        # Determine final response text
        final_text = None
        if latest_review:
            if latest_review.reviewer_decision == ReviewDecisionEnum.EDIT_AND_APPROVE.value:
                final_text = latest_review.edited_response
            elif latest_review.reviewer_decision == ReviewDecisionEnum.APPROVE.value:
                final_text = latest_review.original_ai_response

        grounding_warning = (
            "Cannot approve response because AI grounding validation FAILED. The system requires NEEDS_MORE_EVIDENCE or REJECT until evidence issues are resolved."
            if is_grounding_failed
            else None
        )

        return DisputeReviewStatusResponse(
            dispute_id=dispute.id,
            dispute_reference=dispute.dispute_reference,
            dispute_reason=dispute.dispute_reason,
            dispute_amount=float(dispute.dispute_amount),
            current_status=current_status,
            original_ai_recommendation=ai_resp.recommended_action,
            original_ai_response=ai_resp.draft_response,
            final_response=final_text,
            grounding_status=ai_resp.grounding_status.value,
            can_approve=not is_grounding_failed,
            grounding_warning=grounding_warning,
            latest_review=HumanReviewResponse.model_validate(latest_review) if latest_review else None,
            all_reviews=[HumanReviewResponse.model_validate(r) for r in reviews],
        )

    def submit_review(
        self,
        dispute_ref_or_id: str,
        request: HumanReviewCreateRequest,
    ) -> DisputeReviewStatusResponse:
        """
        Execute human reviewer decision and log corresponding audit events.
        """
        if str(dispute_ref_or_id).isdigit():
            dispute = self.db.query(Dispute).filter(Dispute.id == int(dispute_ref_or_id)).first()
        else:
            dispute = self.db.query(Dispute).filter(Dispute.dispute_reference == str(dispute_ref_or_id)).first()

        if not dispute:
            raise ValueError(f"Dispute '{dispute_ref_or_id}' not found.")

        # 1. Fetch AI Response & verify grounding status
        ai_resp = self.ai_generator.generate_response(str(dispute.id))
        is_grounding_failed = ai_resp.grounding_status == GroundingStatusEnum.FAILED

        # 2. ENFORCE GROUNDING SAFETY RULE
        if request.decision in (ReviewDecisionEnum.APPROVE, ReviewDecisionEnum.EDIT_AND_APPROVE):
            if is_grounding_failed:
                raise ValueError(
                    "Approval rejected: Grounding validation FAILED due to unsupported or non-existent evidence claims. "
                    "You must select 'NEEDS_MORE_EVIDENCE' or 'REJECT' until evidence integrity is established."
                )

        # 3. Decision-Specific Field Validations
        if request.decision == ReviewDecisionEnum.EDIT_AND_APPROVE:
            if not request.edited_response or len(request.edited_response.strip()) < 10:
                raise ValueError("An edited response of at least 10 characters is required for EDIT_AND_APPROVE.")

        if request.decision == ReviewDecisionEnum.NEEDS_MORE_EVIDENCE:
            if not request.reviewer_notes or len(request.reviewer_notes.strip()) < 5:
                raise ValueError("Reviewer notes explaining what evidence is missing are required for NEEDS_MORE_EVIDENCE.")

        # 4. Create HumanReview DB record
        review_record = HumanReview(
            dispute_id=dispute.id,
            reviewer_reference=request.reviewer_reference or "REV-00892",
            original_ai_recommendation=ai_resp.recommended_action,
            original_ai_response=ai_resp.draft_response,
            reviewer_decision=request.decision.value,
            edited_response=request.edited_response if request.decision == ReviewDecisionEnum.EDIT_AND_APPROVE else None,
            reviewer_notes=request.reviewer_notes,
            reviewed_at=datetime.utcnow(),
        )

        self.db.add(review_record)

        # 5. Update dispute status
        if request.decision in (ReviewDecisionEnum.APPROVE, ReviewDecisionEnum.EDIT_AND_APPROVE):
            dispute.dispute_status = "RESOLVED"
        elif request.decision == ReviewDecisionEnum.REJECT:
            dispute.dispute_status = "CLOSED"
        elif request.decision == ReviewDecisionEnum.NEEDS_MORE_EVIDENCE:
            dispute.dispute_status = "UNDER_REVIEW"

        self.db.commit()
        self.db.refresh(review_record)

        # 6. Audit Trail Logging
        if request.decision == ReviewDecisionEnum.APPROVE:
            self.audit_service.log_event(
                dispute.id,
                "REVIEW_APPROVED",
                "HUMAN",
                {"reviewer": review_record.reviewer_reference, "decision": "APPROVE"},
            )
        elif request.decision == ReviewDecisionEnum.EDIT_AND_APPROVE:
            self.audit_service.log_event(
                dispute.id,
                "RESPONSE_EDITED",
                "HUMAN",
                {"reviewer": review_record.reviewer_reference, "edited_length": len(request.edited_response)},
            )
            self.audit_service.log_event(
                dispute.id,
                "REVIEW_APPROVED",
                "HUMAN",
                {"reviewer": review_record.reviewer_reference, "decision": "EDIT_AND_APPROVE"},
            )
        elif request.decision == ReviewDecisionEnum.REJECT:
            self.audit_service.log_event(
                dispute.id,
                "REVIEW_REJECTED",
                "HUMAN",
                {"reviewer": review_record.reviewer_reference, "decision": "REJECT", "notes": request.reviewer_notes},
            )
        elif request.decision == ReviewDecisionEnum.NEEDS_MORE_EVIDENCE:
            self.audit_service.log_event(
                dispute.id,
                "MORE_EVIDENCE_REQUESTED",
                "HUMAN",
                {"reviewer": review_record.reviewer_reference, "notes": request.reviewer_notes},
            )

        return self.get_review_status(str(dispute.id))
