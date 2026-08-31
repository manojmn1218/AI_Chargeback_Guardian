"""
AI Chargeback Guardian — Customer Service
Business logic for synthetic customer operations.
"""

from typing import Optional, Tuple, List
from sqlalchemy.orm import Session

from app.models import Customer
from app.core.logging import logger


class CustomerService:
    """Service layer for synthetic customer operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_customers(
        self,
        page: int = 1,
        page_size: int = 20,
        risk_level: Optional[str] = None,
    ) -> Tuple[List[Customer], int]:
        """Retrieve paginated customers with optional risk filter."""
        query = self.db.query(Customer)
        if risk_level:
            query = query.filter(Customer.customer_risk_history == risk_level.upper())

        total = query.count()
        customers = (
            query.order_by(Customer.id.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        logger.info(f"Retrieved {len(customers)} customers (page {page}, total {total})")
        return customers, total

    def get_customer_by_ref_or_id(self, ref_or_id: str) -> Optional[Customer]:
        """Get customer by reference (e.g. CUST-000001) or primary key ID."""
        if ref_or_id.isdigit():
            customer = self.db.query(Customer).filter(Customer.id == int(ref_or_id)).first()
        else:
            customer = self.db.query(Customer).filter(Customer.customer_reference == ref_or_id).first()

        if customer:
            logger.info(f"Retrieved customer {ref_or_id}")
        else:
            logger.warning(f"Customer {ref_or_id} not found")
        return customer
