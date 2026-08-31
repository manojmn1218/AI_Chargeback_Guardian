"""
AI Chargeback Guardian — Transaction Service
Business logic for synthetic transaction operations.
"""

from typing import Optional, Tuple, List
from sqlalchemy.orm import Session

from app.models import Transaction
from app.core.logging import logger


class TransactionService:
    """Service layer for synthetic transaction operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_transactions(
        self,
        page: int = 1,
        page_size: int = 20,
        customer_id: Optional[int] = None,
        merchant_id: Optional[int] = None,
        payment_method: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Tuple[List[Transaction], int]:
        """Retrieve paginated transactions with optional filters."""
        query = self.db.query(Transaction)
        if customer_id is not None:
            query = query.filter(Transaction.customer_id == customer_id)
        if merchant_id is not None:
            query = query.filter(Transaction.merchant_id == merchant_id)
        if payment_method:
            query = query.filter(Transaction.payment_method_type == payment_method.upper())
        if status:
            query = query.filter(Transaction.transaction_status == status.upper())

        total = query.count()
        transactions = (
            query.order_by(Transaction.transaction_timestamp.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        logger.info(f"Retrieved {len(transactions)} transactions (page {page}, total {total})")
        return transactions, total

    def get_transaction_by_ref_or_id(self, ref_or_id: str) -> Optional[Transaction]:
        """Get transaction by reference (e.g. TXN-000001) or primary key ID."""
        if ref_or_id.isdigit():
            txn = self.db.query(Transaction).filter(Transaction.id == int(ref_or_id)).first()
        else:
            txn = self.db.query(Transaction).filter(Transaction.transaction_reference == ref_or_id).first()

        if txn:
            logger.info(f"Retrieved transaction {ref_or_id}")
        else:
            logger.warning(f"Transaction {ref_or_id} not found")
        return txn
