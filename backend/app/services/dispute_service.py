"""
AI Chargeback Guardian — Dispute Service (Step 2)
Business logic for synthetic dispute operations, evidence retrieval, and communications.
"""

from typing import Optional, Tuple, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func as sql_func

from app.models import Dispute, Evidence, Communication
from app.core.logging import logger


class DisputeService:
    """Service layer for synthetic dispute operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_disputes(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        reason: Optional[str] = None,
        customer_id: Optional[int] = None,
        merchant_id: Optional[int] = None,
    ) -> Tuple[List[Dispute], int]:
        """Retrieve paginated disputes with optional filters."""
        query = self.db.query(Dispute)

        if status:
            query = query.filter(Dispute.dispute_status == status.upper())
        if reason:
            query = query.filter(Dispute.dispute_reason == reason.upper())
        if customer_id is not None:
            query = query.filter(Dispute.customer_id == customer_id)
        if merchant_id is not None:
            query = query.filter(Dispute.merchant_id == merchant_id)

        total = query.count()
        disputes = (
            query
            .order_by(Dispute.dispute_timestamp.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        logger.info(f"Retrieved {len(disputes)} disputes (page {page}, total {total})")
        return disputes, total

    def get_dispute_by_ref_or_id(self, ref_or_id: str) -> Optional[Dispute]:
        """Retrieve detailed dispute with eager relationships by reference or ID."""
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

        if ref_or_id.isdigit():
            dispute = query.filter(Dispute.id == int(ref_or_id)).first()
        else:
            dispute = query.filter(Dispute.dispute_reference == ref_or_id).first()

        if dispute:
            logger.info(f"Retrieved detailed dispute {ref_or_id}")
        else:
            logger.warning(f"Dispute {ref_or_id} not found")
        return dispute

    def get_dispute_evidence(self, ref_or_id: str) -> Tuple[Optional[Dispute], List[Evidence]]:
        """Retrieve evidence items attached to a specific dispute."""
        dispute = self.get_dispute_by_ref_or_id(ref_or_id)
        if not dispute:
            return None, []

        evidence = (
            self.db.query(Evidence)
            .filter(Evidence.dispute_id == dispute.id)
            .order_by(Evidence.id.asc())
            .all()
        )
        return dispute, evidence

    def get_dispute_communications(self, ref_or_id: str) -> Tuple[Optional[Dispute], List[Communication]]:
        """Retrieve communications attached to a specific dispute."""
        dispute = self.get_dispute_by_ref_or_id(ref_or_id)
        if not dispute:
            return None, []

        comms = (
            self.db.query(Communication)
            .filter(Communication.dispute_id == dispute.id)
            .order_by(Communication.communication_timestamp.asc())
            .all()
        )
        return dispute, comms
