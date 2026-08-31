"""
AI Chargeback Guardian — Evidence Intelligence Engine Service (Step 4)

Provides end-to-end evidence retrieval, validation, completeness calculations,
configurable quality scoring, dispute-reason-aware relevance ranking,
chronological timeline synthesis, and consistency anomaly detection.
Uses synthetic SQLite database records only — zero hallucinated evidence.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Dispute,
    Evidence,
    Transaction,
    Customer,
    Merchant,
    Order,
    Delivery,
    Refund,
    Communication,
    MerchantPolicy,
)
from app.schemas.evidence import (
    EvidenceStatusEnum,
    EvidenceCategoryEnum,
    EvidenceItemDetail,
    StrongestEvidenceItem,
    MissingEvidenceItem,
    EvidenceCompletenessMetrics,
    EvidenceSummaryResponse,
    TimelineEvent,
    TimelineResponse,
    ConsistencyWarning,
    MLAnalysisSummary,
    InvestigationDisputeInfo,
    DisputeInvestigationResponse,
)
from app.schemas.entities import (
    CustomerResponse,
    MerchantResponse,
    TransactionResponse,
)
from app.schemas.ml import SHAPFactor
from app.core.logging import logger
from app.services.ml_service import BackendMLService


# Standard 7 Evidence Categories
STANDARD_CATEGORIES = [
    "PAYMENT",
    "INVOICE",
    "ORDER",
    "DELIVERY",
    "REFUND",
    "CUSTOMER_COMMUNICATION",
    "MERCHANT_POLICY",
]

CATEGORY_DISPLAY_NAMES = {
    "PAYMENT": "Payment Authorization & 3DS Log",
    "INVOICE": "Itemized Digital Invoice",
    "ORDER": "Order Confirmation & Cart Receipt",
    "DELIVERY": "Proof of Delivery & Carrier Tracking",
    "REFUND": "Refund Audit & Reversal Records",
    "CUSTOMER_COMMUNICATION": "Customer Support Tickets & Chat",
    "MERCHANT_POLICY": "Terms of Service & Merchant Policy",
}

# Configurable Evidence Quality Weights
# Documented prototype heuristic weights (Availability 35%, Verification 35%, Recency 15%, Source 15%)
DEFAULT_EVIDENCE_WEIGHTS = {
    "availability": 0.35,
    "verification": 0.35,
    "recency": 0.15,
    "source": 0.15,
}

# Configurable Relevance Matrix per Dispute Reason Category
# Prototype heuristic relevance weights (0.0 to 1.0)
RELEVANCE_MATRIX: Dict[str, Dict[str, float]] = {
    "GOODS_NOT_RECEIVED": {
        "DELIVERY": 1.0,
        "CUSTOMER_COMMUNICATION": 0.85,
        "ORDER": 0.75,
        "INVOICE": 0.70,
        "PAYMENT": 0.60,
        "MERCHANT_POLICY": 0.50,
        "REFUND": 0.40,
    },
    "UNAUTHORIZED_TRANSACTION": {
        "PAYMENT": 1.0,
        "CUSTOMER_COMMUNICATION": 0.85,
        "ORDER": 0.80,
        "INVOICE": 0.70,
        "DELIVERY": 0.65,
        "MERCHANT_POLICY": 0.50,
        "REFUND": 0.40,
    },
    "GOODS_NOT_AS_DESCRIBED": {
        "ORDER": 1.0,
        "CUSTOMER_COMMUNICATION": 0.90,
        "MERCHANT_POLICY": 0.85,
        "INVOICE": 0.75,
        "DELIVERY": 0.60,
        "PAYMENT": 0.50,
        "REFUND": 0.40,
    },
    "DUPLICATE_TRANSACTION": {
        "PAYMENT": 1.0,
        "INVOICE": 0.90,
        "ORDER": 0.85,
        "REFUND": 0.80,
        "CUSTOMER_COMMUNICATION": 0.65,
        "MERCHANT_POLICY": 0.50,
        "DELIVERY": 0.40,
    },
    "REFUND_NOT_RECEIVED": {
        "REFUND": 1.0,
        "PAYMENT": 0.85,
        "CUSTOMER_COMMUNICATION": 0.80,
        "INVOICE": 0.65,
        "ORDER": 0.60,
        "MERCHANT_POLICY": 0.55,
        "DELIVERY": 0.40,
    },
}

DEFAULT_RELEVANCE: Dict[str, float] = {
    "PAYMENT": 0.70,
    "INVOICE": 0.70,
    "ORDER": 0.70,
    "DELIVERY": 0.70,
    "REFUND": 0.50,
    "CUSTOMER_COMMUNICATION": 0.70,
    "MERCHANT_POLICY": 0.60,
}


class EvidenceService:
    """Service layer for Evidence Intelligence operations."""

    def __init__(self, db: Session, weights: Optional[Dict[str, float]] = None):
        self.db = db
        self.weights = weights or DEFAULT_EVIDENCE_WEIGHTS

    def get_dispute_with_relations(self, ref_or_id: str) -> Optional[Dispute]:
        """Query dispute with eager relational loads."""
        query = (
            self.db.query(Dispute)
            .options(
                joinedload(Dispute.customer),
                joinedload(Dispute.merchant),
                joinedload(Dispute.transaction),
                joinedload(Dispute.evidence_items),
                joinedload(Dispute.communications),
            )
        )

        if str(ref_or_id).isdigit():
            dispute = query.filter(Dispute.id == int(ref_or_id)).first()
        else:
            dispute = query.filter(Dispute.dispute_reference == str(ref_or_id)).first()

        return dispute

    def calculate_completeness(self, evidence_records: List[Evidence]) -> EvidenceCompletenessMetrics:
        """
        Calculate mathematical evidence completeness metrics.

        Exact calculation:
        - expected_count = 7
        - available_count = count(e for e in evidence if e.available)
        - verified_count = count(e for e in evidence if e.available and e.verified)
        - missing_count = expected_count - available_count
        - availability_percentage = round((available_count / expected_count) * 100, 1)
        - verification_percentage = round((verified_count / expected_count) * 100, 1)
        """
        expected = len(STANDARD_CATEGORIES)
        available = sum(1 for e in evidence_records if e.available)
        verified = sum(1 for e in evidence_records if e.available and e.verified)
        missing = max(0, expected - available)

        avail_pct = round((available / expected) * 100, 1) if expected > 0 else 0.0
        verif_pct = round((verified / expected) * 100, 1) if expected > 0 else 0.0

        # Evidence Quality Score
        quality_score = self.calculate_quality_score(evidence_records, expected, available, verified)

        return EvidenceCompletenessMetrics(
            expected_evidence_count=expected,
            available_evidence_count=available,
            verified_evidence_count=verified,
            missing_evidence_count=missing,
            availability_percentage=avail_pct,
            verification_percentage=verif_pct,
            quality_score=quality_score,
        )

    def calculate_quality_score(
        self,
        evidence_records: List[Evidence],
        expected: int,
        available: int,
        verified: int,
    ) -> float:
        """
        Calculate composite evidence quality score (0.0 to 100.0).

        Components:
        1. Availability component: (available / expected) * w_avail
        2. Verification component: (verified / expected) * w_verif
        3. Recency / Timestamp validity component: valid timestamps ratio * w_recency
        4. Source reference validity: non-empty & valid source ratio * w_source
        """
        if expected == 0:
            return 0.0

        w_avail = self.weights.get("availability", 0.35)
        w_verif = self.weights.get("verification", 0.35)
        w_rec = self.weights.get("recency", 0.15)
        w_src = self.weights.get("source", 0.15)

        avail_ratio = available / expected
        verif_ratio = verified / expected

        if available > 0:
            valid_timestamps = sum(
                1 for e in evidence_records
                if e.available and e.evidence_timestamp is not None
            )
            recency_ratio = valid_timestamps / available

            valid_sources = sum(
                1 for e in evidence_records
                if e.available and e.source_reference and e.source_reference not in ("None on file", "NONE", "")
            )
            source_ratio = valid_sources / available
        else:
            recency_ratio = 0.0
            source_ratio = 0.0

        raw_score = (
            (avail_ratio * w_avail)
            + (verif_ratio * w_verif)
            + (recency_ratio * w_rec)
            + (source_ratio * w_src)
        ) * 100.0

        return round(float(min(100.0, max(0.0, raw_score))), 1)

    def evaluate_evidence_items(
        self,
        dispute_reason: str,
        evidence_records: List[Evidence],
    ) -> Tuple[List[EvidenceItemDetail], List[StrongestEvidenceItem], List[MissingEvidenceItem]]:
        """
        Organize all 7 categories, assign statuses, rank strongest evidence, and identify missing items.
        """
        reason_weights = RELEVANCE_MATRIX.get(dispute_reason.upper(), DEFAULT_RELEVANCE)
        records_by_type = {e.evidence_type.upper(): e for e in evidence_records}

        checklist: List[EvidenceItemDetail] = []
        scored_available_items = []
        missing_items: List[MissingEvidenceItem] = []

        for cat in STANDARD_CATEGORIES:
            display_name = CATEGORY_DISPLAY_NAMES.get(cat, cat)
            rel_score = reason_weights.get(cat, 0.50)
            rec = records_by_type.get(cat)

            if rec and rec.available:
                if rec.verified:
                    status = EvidenceStatusEnum.AVAILABLE_VERIFIED
                    strength_desc = "Verified evidence from authoritative system source"
                else:
                    status = EvidenceStatusEnum.AVAILABLE_UNVERIFIED
                    strength_desc = "Evidence is present but lacks secondary verification"

                # Score item for ranking
                item_score = (rel_score * 0.50) + (0.35 if rec.verified else 0.15) + (0.15 if rec.source_reference else 0.05)

                item_detail = EvidenceItemDetail(
                    id=rec.id,
                    dispute_id=rec.dispute_id,
                    evidence_type=cat,
                    category_display_name=display_name,
                    description=rec.description,
                    source_reference=rec.source_reference or "UNKNOWN_SOURCE",
                    available=True,
                    verified=rec.verified,
                    status=status,
                    evidence_timestamp=rec.evidence_timestamp,
                    relevance_score=round(rel_score, 2),
                    is_strongest=False,
                    strength_rationale=strength_desc,
                )
                checklist.append(item_detail)
                scored_available_items.append((item_score, item_detail, rec))
            else:
                # Missing Category
                status = EvidenceStatusEnum.MISSING
                desc = rec.description if rec else f"No {display_name.lower()} recorded in evidence repository."
                src = rec.source_reference if rec else "None on file"

                # Determine impact of missing evidence
                if rel_score >= 0.85:
                    impact = "HIGH"
                    impact_desc = f"Critical for {dispute_reason.replace('_', ' ')} defense. Issuing bank may uphold chargeback without this record."
                elif rel_score >= 0.65:
                    impact = "MEDIUM"
                    impact_desc = f"Moderately important supporting documentation for contest rebuttal."
                else:
                    impact = "LOW"
                    impact_desc = "Supplemental evidence category. Absence is not fatal to contest submission."

                item_detail = EvidenceItemDetail(
                    id=rec.id if rec else None,
                    dispute_id=rec.dispute_id if rec else None,
                    evidence_type=cat,
                    category_display_name=display_name,
                    description=desc,
                    source_reference=src,
                    available=False,
                    verified=False,
                    status=status,
                    evidence_timestamp=rec.evidence_timestamp if rec else None,
                    relevance_score=round(rel_score, 2),
                    is_strongest=False,
                    strength_rationale=f"Missing evidence item (Impact: {impact})",
                )
                checklist.append(item_detail)
                missing_items.append(
                    MissingEvidenceItem(
                        evidence_type=cat,
                        category_display_name=display_name,
                        impact_level=impact,
                        impact_description=impact_desc,
                    )
                )

        # Sort available items to find strongest (top 3)
        scored_available_items.sort(key=lambda x: x[0], reverse=True)
        strongest_items: List[StrongestEvidenceItem] = []

        for rank, (score, item, rec) in enumerate(scored_available_items[:3], start=1):
            item.is_strongest = True
            rat = (
                f"Rank #{rank}: High relevance ({int(item.relevance_score * 100)}%) for {dispute_reason.replace('_', ' ')} "
                f"with {'verified ' if item.verified else 'unverified '}source '{item.source_reference}'."
            )
            item.strength_rationale = rat

            strongest_items.append(
                StrongestEvidenceItem(
                    evidence_type=item.evidence_type,
                    category_display_name=item.category_display_name,
                    description=item.description,
                    source_reference=item.source_reference,
                    status=item.status,
                    relevance_score=item.relevance_score,
                    rank=rank,
                    rationale=rat,
                )
            )

        return checklist, strongest_items, missing_items

    def generate_timeline(self, dispute: Dispute) -> List[TimelineEvent]:
        """
        Synthesize a chronological investigation timeline from actual relational database records.
        Never invents timestamps; explicitly flags unavailable/missing dates.
        """
        events: List[TimelineEvent] = []
        txn = dispute.transaction
        cust = dispute.customer
        merch = dispute.merchant
        ord_rec = txn.order if txn else None
        deliv = self.db.query(Delivery).filter(Delivery.order_id == ord_rec.id).first() if ord_rec else None
        refund = self.db.query(Refund).filter(Refund.transaction_id == txn.id).first() if txn else None
        comms = self.db.query(Communication).filter(Communication.dispute_id == dispute.id).all()

        # 1. Transaction Event
        if txn:
            events.append(
                TimelineEvent(
                    event_id=f"EVT-TXN-{txn.id}",
                    event_type="TRANSACTION",
                    title="Transaction Authorization",
                    timestamp=txn.transaction_timestamp,
                    timestamp_formatted=txn.transaction_timestamp.strftime("%Y-%m-%d %H:%M:%S") if txn.transaction_timestamp else None,
                    is_available=txn.transaction_timestamp is not None,
                    source=f"GATEWAY ({txn.payment_method_type})",
                    description=f"Transaction of ${txn.amount:.2f} {txn.currency} authorized with status {txn.transaction_status}.",
                    status_badge="AUTHORIZED" if txn.transaction_status == "SUCCESS" else txn.transaction_status,
                )
            )

        # 2. Order Event
        if ord_rec:
            events.append(
                TimelineEvent(
                    event_id=f"EVT-ORD-{ord_rec.id}",
                    event_type="ORDER",
                    title="Order Confirmation",
                    timestamp=ord_rec.order_timestamp,
                    timestamp_formatted=ord_rec.order_timestamp.strftime("%Y-%m-%d %H:%M:%S") if ord_rec.order_timestamp else None,
                    is_available=ord_rec.order_timestamp is not None,
                    source="COMMERCE_ENGINE",
                    description=f"Order #{ord_rec.order_reference} placed for category {ord_rec.product_category} (${ord_rec.order_value:.2f}).",
                    status_badge="FULFILLED" if ord_rec.fulfillment_status == "FULFILLED" else ord_rec.fulfillment_status,
                )
            )

        # 3. Delivery / Shipment Events
        if deliv:
            if deliv.shipped_at:
                events.append(
                    TimelineEvent(
                        event_id=f"EVT-SHIP-{deliv.id}",
                        event_type="SHIPMENT",
                        title="Carrier Dispatch",
                        timestamp=deliv.shipped_at,
                        timestamp_formatted=deliv.shipped_at.strftime("%Y-%m-%d %H:%M:%S"),
                        is_available=True,
                        source="CARRIER_INGESTION",
                        description=f"Consignment handed to courier service (Tracking Available: {deliv.tracking_available}).",
                        status_badge="SHIPPED",
                    )
                )
            else:
                events.append(
                    TimelineEvent(
                        event_id=f"EVT-SHIP-{deliv.id}",
                        event_type="SHIPMENT",
                        title="Carrier Dispatch",
                        timestamp=None,
                        timestamp_formatted=None,
                        is_available=False,
                        source="CARRIER_INGESTION",
                        description="Consignment shipment timestamp not recorded by carrier.",
                        status_badge="MISSING_TIMESTAMP",
                    )
                )

            if deliv.delivered_at:
                events.append(
                    TimelineEvent(
                        event_id=f"EVT-DELIV-{deliv.id}",
                        event_type="DELIVERY",
                        title="Proof of Delivery",
                        timestamp=deliv.delivered_at,
                        timestamp_formatted=deliv.delivered_at.strftime("%Y-%m-%d %H:%M:%S"),
                        is_available=True,
                        source="CARRIER_POD_LOG",
                        description=f"Package delivered (Courier Confirmed: {deliv.delivery_confirmed}, Customer Acknowledged: {deliv.customer_acknowledged}).",
                        status_badge="DELIVERED" if deliv.delivery_confirmed else "UNCONFIRMED",
                    )
                )
            elif deliv.delivery_status == "DELIVERED":
                events.append(
                    TimelineEvent(
                        event_id=f"EVT-DELIV-{deliv.id}",
                        event_type="DELIVERY",
                        title="Proof of Delivery",
                        timestamp=None,
                        timestamp_formatted=None,
                        is_available=False,
                        source="CARRIER_POD_LOG",
                        description="Delivery is marked as delivered, but timestamp is missing in courier database.",
                        status_badge="MISSING_TIMESTAMP",
                    )
                )

        # 4. Refund Event (if exists)
        if refund:
            events.append(
                TimelineEvent(
                    event_id=f"EVT-REFUND-{refund.id}",
                    event_type="REFUND",
                    title="Refund Transaction",
                    timestamp=refund.refund_timestamp,
                    timestamp_formatted=refund.refund_timestamp.strftime("%Y-%m-%d %H:%M:%S") if refund.refund_timestamp else None,
                    is_available=refund.refund_timestamp is not None,
                    source="LEDGER_SETTLEMENT",
                    description=f"Refund of ${refund.refund_amount:.2f} processed. Reason: {refund.refund_reason}.",
                    status_badge="PROCESSED" if refund.refund_status == "PROCESSED" else refund.refund_status,
                )
            )

        # 5. Customer Communications Events
        for c in comms:
            events.append(
                TimelineEvent(
                    event_id=f"EVT-COMM-{c.id}",
                    event_type="COMMUNICATION",
                    title=f"Support Inquiry ({c.communication_type})",
                    timestamp=c.communication_timestamp,
                    timestamp_formatted=c.communication_timestamp.strftime("%Y-%m-%d %H:%M:%S") if c.communication_timestamp else None,
                    is_available=c.communication_timestamp is not None,
                    source="CRM_HELPDESK",
                    description=c.content_summary,
                    status_badge="VERIFIED" if c.verified else "UNVERIFIED",
                )
            )

        # 6. Dispute Filing Event
        events.append(
            TimelineEvent(
                event_id=f"EVT-DISP-{dispute.id}",
                event_type="DISPUTE",
                title=f"Chargeback Filed ({dispute.dispute_reason})",
                timestamp=dispute.dispute_timestamp,
                timestamp_formatted=dispute.dispute_timestamp.strftime("%Y-%m-%d %H:%M:%S") if dispute.dispute_timestamp else None,
                is_available=dispute.dispute_timestamp is not None,
                source="PAYMENT_NETWORK_INCOMING",
                description=f"Dispute claim filed for ${dispute.dispute_amount:.2f} under reason '{dispute.dispute_reason}'. Status: {dispute.dispute_status}.",
                status_badge="OPEN" if dispute.dispute_status == "OPEN" else dispute.dispute_status,
            )
        )

        # Sort events with valid timestamps chronologically; append missing timestamps at end
        dated_events = [e for e in events if e.timestamp is not None]
        undated_events = [e for e in events if e.timestamp is None]

        dated_events.sort(key=lambda x: x.timestamp)
        return dated_events + undated_events

    def run_consistency_checks(self, dispute: Dispute) -> List[ConsistencyWarning]:
        """
        Execute deterministic data integrity and consistency validation rules.
        Flags conflicting timestamps, missing values, and financial mismatches.
        """
        warnings: List[ConsistencyWarning] = []
        txn = dispute.transaction
        ord_rec = txn.order if txn else None
        deliv = self.db.query(Delivery).filter(Delivery.order_id == ord_rec.id).first() if ord_rec else None
        refund = self.db.query(Refund).filter(Refund.transaction_id == txn.id).first() if txn else None

        # Check 1: Delivery marked confirmed but delivery timestamp missing
        if deliv and (deliv.delivery_confirmed or deliv.delivery_status == "DELIVERED") and deliv.delivered_at is None:
            warnings.append(
                ConsistencyWarning(
                    code="DELIVERY_CONFIRMED_NO_TIMESTAMP",
                    severity="HIGH",
                    field="deliveries.delivered_at",
                    message="Delivery status is confirmed delivered, but carrier delivery timestamp is missing.",
                )
            )

        # Check 2: Refund marked completed but refund amount missing or <= 0
        if refund and refund.refund_status == "PROCESSED" and (refund.refund_amount is None or refund.refund_amount <= 0):
            warnings.append(
                ConsistencyWarning(
                    code="REFUND_PROCESSED_INVALID_AMOUNT",
                    severity="HIGH",
                    field="refunds.refund_amount",
                    message="Refund is marked as PROCESSED, but refund amount is missing or invalid.",
                )
            )

        # Check 3: Dispute amount differs from transaction amount
        if txn and dispute.dispute_amount is not None and txn.amount is not None:
            diff = round(abs(dispute.dispute_amount - txn.amount), 2)
            if diff > 0.01:
                warnings.append(
                    ConsistencyWarning(
                        code="AMOUNT_MISMATCH",
                        severity="MEDIUM",
                        field="disputes.dispute_amount",
                        message=f"Dispute amount (${dispute.dispute_amount:.2f}) differs from transaction amount (${txn.amount:.2f}) by ${diff:.2f}.",
                    )
                )

        # Check 4: Delivery date occurs before order date
        if deliv and deliv.delivered_at and ord_rec and ord_rec.order_timestamp:
            if deliv.delivered_at < ord_rec.order_timestamp:
                warnings.append(
                    ConsistencyWarning(
                        code="DELIVERY_BEFORE_ORDER",
                        severity="CRITICAL",
                        field="deliveries.delivered_at",
                        message=f"Delivery timestamp ({deliv.delivered_at}) occurs before order placement timestamp ({ord_rec.order_timestamp}).",
                    )
                )

        # Check 5: Shipped date occurs before transaction date
        if deliv and deliv.shipped_at and txn and txn.transaction_timestamp:
            if deliv.shipped_at < txn.transaction_timestamp:
                warnings.append(
                    ConsistencyWarning(
                        code="SHIPMENT_BEFORE_TRANSACTION",
                        severity="HIGH",
                        field="deliveries.shipped_at",
                        message=f"Consignment shipment timestamp ({deliv.shipped_at}) precedes transaction authorization ({txn.transaction_timestamp}).",
                    )
                )

        # Check 6: Refund date occurs before transaction date
        if refund and refund.refund_timestamp and txn and txn.transaction_timestamp:
            if refund.refund_timestamp < txn.transaction_timestamp:
                warnings.append(
                    ConsistencyWarning(
                        code="REFUND_BEFORE_TRANSACTION",
                        severity="HIGH",
                        field="refunds.refund_timestamp",
                        message=f"Refund settlement timestamp ({refund.refund_timestamp}) precedes transaction authorization ({txn.transaction_timestamp}).",
                    )
                )

        # Check 7: Dispute date occurs before transaction date
        if dispute.dispute_timestamp and txn and txn.transaction_timestamp:
            if dispute.dispute_timestamp < txn.transaction_timestamp:
                warnings.append(
                    ConsistencyWarning(
                        code="DISPUTE_BEFORE_TRANSACTION",
                        severity="CRITICAL",
                        field="disputes.dispute_timestamp",
                        message=f"Dispute filing timestamp ({dispute.dispute_timestamp}) precedes original transaction authorization ({txn.transaction_timestamp}).",
                    )
                )

        return warnings

    def get_evidence_summary(self, ref_or_id: str) -> EvidenceSummaryResponse:
        """
        Generate structured evidence summary for a dispute.
        """
        dispute = self.get_dispute_with_relations(ref_or_id)
        if not dispute:
            raise ValueError(f"Dispute '{ref_or_id}' not found.")

        evidence_records = dispute.evidence_items or []
        metrics = self.calculate_completeness(evidence_records)
        checklist, strongest, missing = self.evaluate_evidence_items(dispute.dispute_reason, evidence_records)

        return EvidenceSummaryResponse(
            dispute_id=dispute.id,
            dispute_reference=dispute.dispute_reference,
            dispute_reason=dispute.dispute_reason,
            total_expected=metrics.expected_evidence_count,
            available=metrics.available_evidence_count,
            verified=metrics.verified_evidence_count,
            missing=metrics.missing_evidence_count,
            availability_percentage=metrics.availability_percentage,
            verification_percentage=metrics.verification_percentage,
            quality_score=metrics.quality_score,
            strongest_evidence=strongest,
            missing_evidence=missing,
            evidence_checklist=checklist,
        )

    def get_timeline_response(self, ref_or_id: str) -> TimelineResponse:
        """
        Generate timeline response for a dispute.
        """
        dispute = self.get_dispute_with_relations(ref_or_id)
        if not dispute:
            raise ValueError(f"Dispute '{ref_or_id}' not found.")

        timeline_events = self.generate_timeline(dispute)

        return TimelineResponse(
            dispute_id=dispute.id,
            dispute_reference=dispute.dispute_reference,
            events_count=len(timeline_events),
            timeline=timeline_events,
        )

    def get_investigation(self, ref_or_id: str) -> DisputeInvestigationResponse:
        """
        Generate full combined investigation result:
        - Dispute details with Customer, Merchant, and Transaction
        - Step 3 ML Prediction & SHAP analysis
        - Evidence completeness, quality score, strongest & missing evidence
        - Chronological investigation timeline
        - Consistency check warnings
        """
        dispute = self.get_dispute_with_relations(ref_or_id)
        if not dispute:
            raise ValueError(f"Dispute '{ref_or_id}' not found.")

        # 1. Evidence analysis
        evidence_records = dispute.evidence_items or []
        metrics = self.calculate_completeness(evidence_records)
        checklist, strongest, missing = self.evaluate_evidence_items(dispute.dispute_reason, evidence_records)

        evidence_summary = EvidenceSummaryResponse(
            dispute_id=dispute.id,
            dispute_reference=dispute.dispute_reference,
            dispute_reason=dispute.dispute_reason,
            total_expected=metrics.expected_evidence_count,
            available=metrics.available_evidence_count,
            verified=metrics.verified_evidence_count,
            missing=metrics.missing_evidence_count,
            availability_percentage=metrics.availability_percentage,
            verification_percentage=metrics.verification_percentage,
            quality_score=metrics.quality_score,
            strongest_evidence=strongest,
            missing_evidence=missing,
            evidence_checklist=checklist,
        )

        # 2. Timeline
        timeline_events = self.generate_timeline(dispute)

        # 3. Warnings
        warnings = self.run_consistency_checks(dispute)

        # 4. ML Prediction from Step 3 BackendMLService
        ml_summary: Optional[MLAnalysisSummary] = None
        try:
            backend_ml = BackendMLService(self.db)
            ml_pred = backend_ml.score_dispute_by_id(str(dispute.id))

            pos_factors = [
                SHAPFactor(
                    feature=f["feature"],
                    display_name=f["display_name"],
                    contribution=f["contribution"],
                    impact=f["impact"],
                    positive=f["positive"],
                )
                for f in ml_pred.get("top_positive_factors", [])
            ]

            neg_factors = [
                SHAPFactor(
                    feature=f["feature"],
                    display_name=f["display_name"],
                    contribution=f["contribution"],
                    impact=f["impact"],
                    positive=f["positive"],
                )
                for f in ml_pred.get("top_negative_factors", [])
            ]

            ml_summary = MLAnalysisSummary(
                probability=ml_pred["case_strength_probability"],
                score=ml_pred["case_strength_score"],
                classification=ml_pred["classification"],
                recommend_contest=ml_pred["recommend_contest"],
                threshold=ml_pred["threshold"],
                model_version=ml_pred["model_version"],
                model_name=ml_pred["model_name"],
                top_positive_factors=pos_factors,
                top_negative_factors=neg_factors,
                disclaimer=ml_pred["disclaimer"],
            )
        except Exception as e:
            logger.warning(f"ML analysis could not be scored for dispute {dispute.id}: {e}")
            ml_summary = None

        # 5. Build enriched dispute info
        cust_resp = CustomerResponse.model_validate(dispute.customer) if dispute.customer else None
        merch_resp = MerchantResponse.model_validate(dispute.merchant) if dispute.merchant else None
        txn_resp = TransactionResponse.model_validate(dispute.transaction) if dispute.transaction else None

        dispute_info = InvestigationDisputeInfo(
            id=dispute.id,
            dispute_reference=dispute.dispute_reference,
            transaction_id=dispute.transaction_id,
            customer_id=dispute.customer_id,
            merchant_id=dispute.merchant_id,
            dispute_reason=dispute.dispute_reason,
            dispute_amount=dispute.dispute_amount,
            dispute_status=dispute.dispute_status,
            dispute_timestamp=dispute.dispute_timestamp,
            outcome=dispute.outcome,
            created_at=dispute.created_at,
            customer=cust_resp,
            merchant=merch_resp,
            transaction=txn_resp,
        )

        return DisputeInvestigationResponse(
            dispute=dispute_info,
            ml_analysis=ml_summary,
            evidence_analysis=evidence_summary,
            timeline=timeline_events,
            warnings=warnings,
        )
