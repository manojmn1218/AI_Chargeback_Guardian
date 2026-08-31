"""
AI Chargeback Guardian — Grounding Validation Service (Step 5)

Performs deterministic anti-hallucination and evidence-integrity checks on AI output:
1. Validates that every cited evidence/policy reference exists and belongs to the dispute.
2. Checks for unsupported factual claims (e.g., claiming delivery was confirmed when delivery_confirmed=False).
3. Checks that missing records are not cited as available proof.
4. Checks that unverified records are not claimed as verified facts.
5. Returns strict GroundingValidationDetail with status VERIFIED, REVIEW_REQUIRED, or FAILED.
"""

import re
from typing import Dict, Any, List, Set
from app.schemas.ai import GroundingStatusEnum, GroundingValidationDetail, AIResponseOutput


class GroundingValidator:
    """
    Deterministic validator to ensure generated drafts contain zero hallucinations.
    """

    @classmethod
    def validate(cls, ai_output: AIResponseOutput, context: Dict[str, Any]) -> GroundingValidationDetail:
        """
        Validate generated AI output against the grounded context.
        """
        passed_checks: List[str] = []
        failed_checks: List[str] = []
        issues: List[str] = []

        allowed_refs: Set[str] = set(context.get("allowed_evidence_references", []))
        delivery_state = context.get("delivery_state", {})
        refund_state = context.get("refund_state", {})
        missing_ev = context.get("missing_evidence", [])
        missing_types = {m["evidence_type"].upper() for m in missing_ev}

        draft_text = ai_output.draft_response
        full_text_to_check = f"{ai_output.case_summary} {' '.join(ai_output.key_verified_facts)} {draft_text}".lower()

        # ==========================================
        # Check 1: Evidence References Traceability
        # ==========================================
        # Extract all [EVIDENCE: ...] and [POLICY: ...] citations
        cited_in_draft = set(re.findall(r"\[(?:EVIDENCE|POLICY):\s*[A-Za-z0-9_\-]+\]", draft_text, flags=re.IGNORECASE))
        cited_in_list = set(ai_output.evidence_references or [])
        all_cited = {r.upper() for r in (cited_in_draft | cited_in_list)}

        valid_refs: List[str] = []
        invalid_refs: List[str] = []

        for ref in all_cited:
            normalized_ref = ref.strip()
            # Normalize spacing e.g. "[EVIDENCE:DELIVERY]" -> "[EVIDENCE: DELIVERY]"
            clean_ref = re.sub(r":\s*", ": ", normalized_ref)
            if clean_ref in allowed_refs or any(clean_ref in a for a in allowed_refs):
                valid_refs.append(clean_ref)
            else:
                invalid_refs.append(clean_ref)

        if invalid_refs:
            failed_checks.append("EVIDENCE_REFERENCE_EXISTENCE")
            issues.append(f"Response cited {len(invalid_refs)} unverified or non-existent evidence reference(s): {', '.join(invalid_refs)}")
        else:
            passed_checks.append("EVIDENCE_REFERENCE_EXISTENCE")

        # ==========================================
        # Check 2: Delivery Confirmation Claim Rule
        # ==========================================
        is_delivery_confirmed = delivery_state.get("delivery_confirmed", False)
        delivery_claim_patterns = [
            r"delivery\s+was\s+confirmed",
            r"delivered\s+successfully",
            r"delivery\s+has\s+been\s+confirmed",
            r"confirmed\s+delivery",
            r"carrier\s+confirmed\s+delivery",
            r"package\s+was\s+delivered\s+to\s+the\s+customer",
        ]

        has_delivery_claim = any(re.search(pat, full_text_to_check) for pat in delivery_claim_patterns)

        if not is_delivery_confirmed and has_delivery_claim:
            failed_checks.append("UNSUPPORTED_DELIVERY_CLAIM")
            issues.append("Response claimed delivery was confirmed, but delivery_confirmed is False in database.")
        else:
            passed_checks.append("UNSUPPORTED_DELIVERY_CLAIM")

        # ==========================================
        # Check 3: Refund Processed Claim Rule
        # ==========================================
        is_refund_processed = (
            refund_state.get("refund_recorded", False)
            and refund_state.get("refund_status", "").upper() == "PROCESSED"
        )
        refund_claim_patterns = [
            r"refund\s+was\s+processed",
            r"refund\s+has\s+been\s+processed",
            r"refund\s+was\s+issued",
            r"refund\s+has\s+been\s+issued",
            r"refund\s+completed",
            r"settled\s+a\s+refund",
        ]

        has_refund_claim = any(re.search(pat, full_text_to_check) for pat in refund_claim_patterns)

        if not is_refund_processed and has_refund_claim:
            failed_checks.append("UNSUPPORTED_REFUND_CLAIM")
            issues.append("Response claimed a refund was processed, but no processed refund record exists in database.")
        else:
            passed_checks.append("UNSUPPORTED_REFUND_CLAIM")

        # ==========================================
        # Check 4: Customer Acknowledgement Claim Rule
        # ==========================================
        is_cust_acknowledged = delivery_state.get("customer_acknowledged", False)
        ack_claim_patterns = [
            r"customer\s+acknowledged\s+receipt",
            r"customer\s+confirmed\s+receipt",
            r"customer\s+acknowledged\s+receiving",
            r"customer\s+confirmed\s+receiving",
        ]

        has_ack_claim = any(re.search(pat, full_text_to_check) for pat in ack_claim_patterns)

        if not is_cust_acknowledged and has_ack_claim:
            failed_checks.append("UNSUPPORTED_CUSTOMER_ACK_CLAIM")
            issues.append("Response claimed customer acknowledged receipt, but customer_acknowledged is False in database.")
        else:
            passed_checks.append("UNSUPPORTED_CUSTOMER_ACK_CLAIM")

        # ==========================================
        # Check 5: Missing Evidence Factual Claim Rule
        # ==========================================
        missing_claimed_verified = False
        for fact in ai_output.key_verified_facts:
            fact_upper = fact.upper()
            for m_type in missing_types:
                if f"[EVIDENCE: {m_type}]" in fact_upper or f"EVIDENCE: {m_type}" in fact_upper:
                    missing_claimed_verified = True
                    issues.append(f"Missing evidence category '{m_type}' was cited as a verified fact.")

        if missing_claimed_verified:
            failed_checks.append("MISSING_EVIDENCE_NOT_VERIFIED")
        else:
            passed_checks.append("MISSING_EVIDENCE_NOT_VERIFIED")

        # ==========================================
        # Determine Overall Grounding Status
        # ==========================================
        if failed_checks:
            # Critical violations fail grounding
            if any(c in failed_checks for c in ("UNSUPPORTED_DELIVERY_CLAIM", "UNSUPPORTED_REFUND_CLAIM", "UNSUPPORTED_CUSTOMER_ACK_CLAIM", "EVIDENCE_REFERENCE_EXISTENCE")):
                status = GroundingStatusEnum.FAILED
                is_valid = False
            else:
                status = GroundingStatusEnum.REVIEW_REQUIRED
                is_valid = False
        else:
            status = GroundingStatusEnum.VERIFIED
            is_valid = True

        return GroundingValidationDetail(
            is_valid=is_valid,
            status=status,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            issues=issues,
            checked_references_count=len(all_cited),
            valid_references=valid_refs,
            invalid_references=invalid_refs,
        )
