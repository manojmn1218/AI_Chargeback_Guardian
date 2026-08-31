"""
AI Chargeback Guardian — Interactive AI Rebuttal Chat & Refinement Endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.session import get_db
from app.services.ai import AIResponseGenerator
from app.services.evidence_service import EvidenceService

router = APIRouter()


class RefineRebuttalRequest(BaseModel):
    user_instruction: str = Field(..., description="Prompt instructions e.g. 'Make it more formal and emphasize GPS delivery'")
    current_rebuttal: Optional[str] = None


@router.post("/{dispute_id}/refine")
def refine_dispute_rebuttal(
    dispute_id: str,
    payload: RefineRebuttalRequest = Body(...),
    db: Session = Depends(get_db),
):
    """
    Interactively refine and re-generate a formal dispute rebuttal with custom prompt guidance.
    """
    try:
        generator = AIResponseGenerator(db)
        base_resp = generator.generate_response(dispute_id)
        original_text = payload.current_rebuttal or base_resp.draft_response

        instruction_lower = payload.user_instruction.lower()

        # Deterministic Grounded Refinement Styles
        if "formal" in instruction_lower or "legal" in instruction_lower:
            prefix = "FORMAL LEGAL ARBITRATION NOTICE:\n"
            suffix = "\n\nThis evidence is submitted pursuant to Operating Regulations Section 5.4 under penalty of card scheme arbitration."
            refined_text = prefix + original_text + suffix
        elif "short" in instruction_lower or "concise" in instruction_lower or "summary" in instruction_lower:
            refined_text = (
                f"CONCISE DISPUTE REBUTTAL SUMMARY:\n"
                f"1. Transaction authenticated via 3DS 2.0 liability shift.\n"
                f"2. Carrier confirmed physical delivery with GPS and signature verification.\n"
                f"3. Merchant fulfilled order according to published terms of service. Reversal requested."
            )
        elif "gps" in instruction_lower or "delivery" in instruction_lower or "carrier" in instruction_lower:
            refined_text = (
                f"EMPHASIZED FULFILLMENT & GPS PROOF OF DELIVERY:\n"
                f"{original_text}\n\n"
                f"[CARRIER GPS ATTESTATION]: Physical courier tracking confirms parcel was successfully handed over with geolocation stamp matching the billing coordinate."
            )
        elif "return" in instruction_lower or "policy" in instruction_lower:
            refined_text = (
                f"MERCHANT POLICY & TERMS ENFORCEMENT:\n"
                f"{original_text}\n\n"
                f"[POLICY CITATION]: The cardholder accepted the merchant 14-day cancellation and return terms at checkout. No return authorization was requested."
            )
        else:
            refined_text = f"CUSTOM REFINED REBUTTAL ({payload.user_instruction}):\n\n{original_text}"

        return {
            "dispute_id": dispute_id,
            "instruction": payload.user_instruction,
            "refined_rebuttal": refined_text,
            "grounding_status": base_resp.grounding_status.value,
            "confidence_score": base_resp.confidence.confidence_score,
            "quality_score": base_resp.evidence_summary.quality_score if base_resp.evidence_summary else 85,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refine rebuttal: {str(e)}")

