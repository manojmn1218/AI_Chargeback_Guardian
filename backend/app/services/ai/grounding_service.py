"""
AI Chargeback Guardian — Evidence Grounding Service (Step 5)

Responsibilities:
1. Ingest investigation data from Step 4 Evidence Service.
2. Strictly partition evidence into VERIFIED_FACT, UNVERIFIED_INFORMATION, and MISSING_INFORMATION.
3. Retrieve relevant merchant policies based on dispute reason.
4. Exclude missing evidence from factual claims.
5. Sanitize database and user texts to defend against prompt injection.
6. Produce a compact, authoritative Grounded Context object for the LLM.
"""

import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models import MerchantPolicy, Dispute, Delivery, Refund
from app.services.evidence_service import EvidenceService
from app.schemas.evidence import DisputeInvestigationResponse, EvidenceItemDetail, EvidenceStatusEnum


# Policy relevance mapping by dispute reason
POLICY_RELEVANCE_MAPPING = {
    "GOODS_NOT_RECEIVED": ["SHIPPING_POLICY", "TERMS_OF_SERVICE", "REFUND_POLICY"],
    "REFUND_NOT_RECEIVED": ["REFUND_POLICY", "CANCELLATION_POLICY", "TERMS_OF_SERVICE"],
    "GOODS_NOT_AS_DESCRIBED": ["TERMS_OF_SERVICE", "REFUND_POLICY", "CANCELLATION_POLICY"],
    "DUPLICATE_TRANSACTION": ["TERMS_OF_SERVICE", "REFUND_POLICY"],
    "UNAUTHORIZED_TRANSACTION": ["TERMS_OF_SERVICE"],
}


def sanitize_untrusted_text(text: Optional[str]) -> str:
    """
    Sanitize text fields from database or user inputs to neutralize potential prompt injection.
    Treats database evidence strictly as data tokens, not executable instructions.
    """
    if not text:
        return ""

    # Replace instruction overrides
    sanitized = text
    suspicious_patterns = [
        r"ignore\s+(all\s+)?(previous|above)\s+instructions",
        r"system\s*prompt\s*:",
        r"<\/?(system|assistant|user|context|evidence_data)[^>]*>",
        r"you\s+are\s+now\s+",
        r"disregard\s+the\s+rules",
        r"admin\s+mode",
    ]

    for pattern in suspicious_patterns:
        sanitized = re.sub(pattern, "[UNTRUSTED_CONTENT_FILTERED]", sanitized, flags=re.IGNORECASE)

    # Escape angle brackets to prevent XML/HTML confusion
    sanitized = sanitized.replace("<", "[").replace(">", "]")
    return sanitized.strip()


class EvidenceGroundingService:
    """
    Grounding service that prepares immutable factual context from SQLite records.
    """

    def __init__(self, db: Session):
        self.db = db
        self.evidence_service = EvidenceService(db)

    def retrieve_merchant_policies(self, merchant_id: Optional[int], dispute_reason: str) -> List[Dict[str, Any]]:
        """
        Lightweight RAG retrieval for active merchant policies relevant to this dispute reason.
        """
        if not merchant_id:
            return []

        # Query all active policies for merchant
        policies = (
            self.db.query(MerchantPolicy)
            .filter(
                MerchantPolicy.merchant_id == merchant_id,
                MerchantPolicy.active == True,
            )
            .all()
        )

        if not policies:
            return []

        preferred_types = POLICY_RELEVANCE_MAPPING.get(dispute_reason.upper(), ["TERMS_OF_SERVICE", "REFUND_POLICY"])

        policy_results = []
        for p in policies:
            p_type = p.policy_type.upper()
            relevance = 1.0 if p_type in preferred_types else 0.5
            policy_results.append({
                "id": p.id,
                "merchant_id": p.merchant_id,
                "policy_type": p_type,
                "policy_text": sanitize_untrusted_text(p.policy_text),
                "source_reference": f"[POLICY: {p_type}]",
                "relevance_score": relevance,
                "is_priority": p_type in preferred_types,
            })

        # Sort priority policies first
        policy_results.sort(key=lambda x: (x["relevance_score"], x["is_priority"]), reverse=True)
        return policy_results

    def build_grounded_context(self, dispute_ref_or_id: str) -> Dict[str, Any]:
        """
        Compile full investigation into a grounded context dictionary.
        Separates verified facts from unverified and missing items.
        """
        investigation: DisputeInvestigationResponse = self.evidence_service.get_investigation(dispute_ref_or_id)
        dispute = investigation.dispute
        ev_analysis = investigation.evidence_analysis

        # 1. Retrieve policies
        merchant_id = dispute.merchant_id or (dispute.merchant.id if dispute.merchant else None)
        policies = self.retrieve_merchant_policies(merchant_id, dispute.dispute_reason)

        # 2. Separate verified vs unverified vs missing
        verified_evidence: List[Dict[str, Any]] = []
        unverified_evidence: List[Dict[str, Any]] = []
        missing_evidence: List[Dict[str, Any]] = []
        allowed_references: List[str] = []

        checklist = ev_analysis.evidence_checklist or []
        for item in checklist:
            item_dict = {
                "id": item.id,
                "evidence_type": item.evidence_type,
                "display_name": item.category_display_name,
                "description": sanitize_untrusted_text(item.description),
                "source_reference": sanitize_untrusted_text(item.source_reference),
                "status": item.status,
                "timestamp": item.evidence_timestamp.isoformat() if item.evidence_timestamp else None,
                "reference_tag": f"[EVIDENCE: {item.evidence_type}]",
            }

            if item.status == EvidenceStatusEnum.AVAILABLE_VERIFIED:
                verified_evidence.append(item_dict)
                allowed_references.append(f"[EVIDENCE: {item.evidence_type}]")
            elif item.status == EvidenceStatusEnum.AVAILABLE_UNVERIFIED:
                unverified_evidence.append(item_dict)
                allowed_references.append(f"[EVIDENCE: {item.evidence_type}]")
            else:
                missing_evidence.append({
                    "evidence_type": item.evidence_type,
                    "display_name": item.category_display_name,
                    "impact_rationale": sanitize_untrusted_text(item.strength_rationale),
                })

        for p in policies:
            allowed_references.append(p["source_reference"])

        # 3. Delivery & Refund states for strict deterministic verification
        db_dispute = self.evidence_service.get_dispute_with_relations(dispute_ref_or_id)
        txn = db_dispute.transaction if db_dispute else None
        ord_rec = txn.order if txn else None
        deliv = self.db.query(Delivery).filter(Delivery.order_id == ord_rec.id).first() if ord_rec else None
        refund = self.db.query(Refund).filter(Refund.transaction_id == txn.id).first() if txn else None

        delivery_state = {
            "delivery_recorded": deliv is not None,
            "delivery_status": deliv.delivery_status if deliv else "UNKNOWN",
            "delivery_confirmed": bool(deliv.delivery_confirmed) if deliv else False,
            "customer_acknowledged": bool(deliv.customer_acknowledged) if deliv else False,
            "tracking_available": bool(deliv.tracking_available) if deliv else False,
            "shipped_at": deliv.shipped_at.isoformat() if deliv and deliv.shipped_at else None,
            "delivered_at": deliv.delivered_at.isoformat() if deliv and deliv.delivered_at else None,
        }

        refund_state = {
            "refund_recorded": refund is not None,
            "refund_status": refund.refund_status if refund else "NONE",
            "refund_amount": float(refund.refund_amount) if refund else 0.0,
            "refund_timestamp": refund.refund_timestamp.isoformat() if refund and refund.refund_timestamp else None,
            "refund_reason": sanitize_untrusted_text(refund.refund_reason) if refund else "",
        }

        # 4. Warnings
        warnings_list = [
            {
                "code": w.code,
                "severity": w.severity,
                "field": w.field,
                "message": sanitize_untrusted_text(w.message),
            }
            for w in (investigation.warnings or [])
        ]

        # 5. Timeline summary
        timeline_events = [
            {
                "event_id": t.event_id,
                "event_type": t.event_type,
                "title": t.title,
                "timestamp": t.timestamp_formatted or "MISSING_TIMESTAMP",
                "source": sanitize_untrusted_text(t.source),
                "description": sanitize_untrusted_text(t.description),
                "is_available": t.is_available,
            }
            for t in (investigation.timeline or [])
        ]

        return {
            "dispute": {
                "id": dispute.id,
                "dispute_reference": dispute.dispute_reference,
                "dispute_reason": dispute.dispute_reason,
                "dispute_amount": float(dispute.dispute_amount),
                "currency": "USD",
                "dispute_status": dispute.dispute_status,
                "dispute_timestamp": dispute.dispute_timestamp.isoformat() if dispute.dispute_timestamp else None,
            },
            "transaction": {
                "transaction_reference": dispute.transaction.transaction_reference if dispute.transaction else f"TXN-{dispute.transaction_id}",
                "amount": float(dispute.transaction.amount) if dispute.transaction else float(dispute.dispute_amount),
                "currency": dispute.transaction.currency if dispute.transaction else "USD",
                "payment_method_type": dispute.transaction.payment_method_type if dispute.transaction else "CREDIT_CARD",
                "device_reference": dispute.transaction.device_reference if dispute.transaction else "UNKNOWN",
                "location_region": dispute.transaction.location_region if dispute.transaction else "UNKNOWN",
                "transaction_timestamp": dispute.transaction.transaction_timestamp.isoformat() if dispute.transaction and dispute.transaction.transaction_timestamp else None,
            },
            "customer": {
                "customer_reference": dispute.customer.customer_reference if dispute.customer else f"CUST-{dispute.customer_id}",
                "account_age_days": dispute.customer.account_age_days if dispute.customer else 0,
                "previous_disputes": dispute.customer.previous_disputes if dispute.customer else 0,
                "previous_successful_transactions": dispute.customer.previous_successful_transactions if dispute.customer else 0,
                "risk_history": dispute.customer.customer_risk_history if dispute.customer else "LOW",
            },
            "merchant": {
                "merchant_reference": dispute.merchant.merchant_reference if dispute.merchant else f"MER-{dispute.merchant_id}",
                "merchant_category": dispute.merchant.merchant_category if dispute.merchant else "RETAIL",
                "dispute_rate": float(dispute.merchant.historical_dispute_rate) if dispute.merchant else 0.01,
            },
            "delivery_state": delivery_state,
            "refund_state": refund_state,
            "verified_evidence": verified_evidence,
            "unverified_evidence": unverified_evidence,
            "missing_evidence": missing_evidence,
            "merchant_policies": policies,
            "allowed_evidence_references": allowed_references,
            "warnings": warnings_list,
            "timeline": timeline_events,
            "ml_analysis": investigation.ml_analysis.model_dump() if investigation.ml_analysis else None,
            "evidence_summary": investigation.evidence_analysis.model_dump() if investigation.evidence_analysis else None,
        }
