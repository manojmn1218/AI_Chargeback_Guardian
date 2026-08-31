"""
AI Chargeback Guardian — Merchant Service
Business logic for synthetic merchant operations.
"""

from typing import Optional, Tuple, List
from sqlalchemy.orm import Session

from app.models import Merchant
from app.core.logging import logger


class MerchantService:
    """Service layer for synthetic merchant operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_merchants(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
    ) -> Tuple[List[Merchant], int]:
        """Retrieve paginated merchants with optional category filter."""
        query = self.db.query(Merchant)
        if category:
            query = query.filter(Merchant.merchant_category == category.upper())

        total = query.count()
        merchants = (
            query.order_by(Merchant.id.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        logger.info(f"Retrieved {len(merchants)} merchants (page {page}, total {total})")
        return merchants, total

    def get_merchant_by_ref_or_id(self, ref_or_id: str) -> Optional[Merchant]:
        """Get merchant by reference (e.g. MER-000001) or primary key ID."""
        if ref_or_id.isdigit():
            merchant = self.db.query(Merchant).filter(Merchant.id == int(ref_or_id)).first()
        else:
            merchant = self.db.query(Merchant).filter(Merchant.merchant_reference == ref_or_id).first()

        if merchant:
            logger.info(f"Retrieved merchant {ref_or_id}")
        else:
            logger.warning(f"Merchant {ref_or_id} not found")
        return merchant
