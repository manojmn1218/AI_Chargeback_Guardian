"""
AI Chargeback Guardian — Transactions Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.session import get_db
from app.models import Transaction
from app.schemas import TransactionResponse, TransactionListResponse

router = APIRouter()


@router.get("", response_model=TransactionListResponse)
def list_transactions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    merchant_id: Optional[int] = Query(None, description="Filter by merchant ID"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method"),
    db: Session = Depends(get_db),
):
    """List synthetic transactions with pagination and optional filters."""
    query = db.query(Transaction)
    if customer_id:
        query = query.filter(Transaction.customer_id == customer_id)
    if merchant_id:
        query = query.filter(Transaction.merchant_id == merchant_id)
    if payment_method:
        query = query.filter(Transaction.payment_method_type == payment_method.upper())

    total = query.count()
    items = (
        query.order_by(Transaction.transaction_timestamp.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return TransactionListResponse(
        items=[TransactionResponse.model_validate(t) for t in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{txn_ref_or_id}", response_model=TransactionResponse)
def get_transaction(txn_ref_or_id: str, db: Session = Depends(get_db)):
    """Get transaction details by reference (e.g. TXN-000001) or primary key ID."""
    if txn_ref_or_id.isdigit():
        txn = db.query(Transaction).filter(Transaction.id == int(txn_ref_or_id)).first()
    else:
        txn = db.query(Transaction).filter(Transaction.transaction_reference == txn_ref_or_id).first()

    if not txn:
        raise HTTPException(status_code=404, detail=f"Transaction {txn_ref_or_id} not found")

    return TransactionResponse.model_validate(txn)
