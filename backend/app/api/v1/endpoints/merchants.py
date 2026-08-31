"""
AI Chargeback Guardian — Merchants Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.session import get_db
from app.models import Merchant
from app.schemas import MerchantResponse, MerchantListResponse

router = APIRouter()


@router.get("", response_model=MerchantListResponse)
def list_merchants(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by merchant category"),
    db: Session = Depends(get_db),
):
    """List synthetic merchants with pagination and category filtering."""
    query = db.query(Merchant)
    if category:
        query = query.filter(Merchant.merchant_category == category.upper())

    total = query.count()
    items = (
        query.order_by(Merchant.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return MerchantListResponse(
        items=[MerchantResponse.model_validate(m) for m in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{merchant_ref_or_id}", response_model=MerchantResponse)
def get_merchant(merchant_ref_or_id: str, db: Session = Depends(get_db)):
    """Get merchant details by reference (e.g. MER-000001) or primary key ID."""
    if merchant_ref_or_id.isdigit():
        merchant = db.query(Merchant).filter(Merchant.id == int(merchant_ref_or_id)).first()
    else:
        merchant = db.query(Merchant).filter(Merchant.merchant_reference == merchant_ref_or_id).first()

    if not merchant:
        raise HTTPException(status_code=404, detail=f"Merchant {merchant_ref_or_id} not found")

    return MerchantResponse.model_validate(merchant)
