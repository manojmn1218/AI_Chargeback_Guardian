"""
AI Chargeback Guardian — Customers Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.session import get_db
from app.services.customer_service import CustomerService
from app.schemas import CustomerResponse, CustomerListResponse

router = APIRouter()


@router.get("", response_model=CustomerListResponse)
def list_customers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    risk_level: Optional[str] = Query(None, description="Filter by risk profile (LOW, MEDIUM, HIGH)"),
    db: Session = Depends(get_db),
):
    """List synthetic customers with pagination and optional risk filter."""
    service = CustomerService(db)
    customers, total = service.get_customers(page=page, page_size=page_size, risk_level=risk_level)

    return CustomerListResponse(
        items=[CustomerResponse.model_validate(c) for c in customers],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{customer_ref_or_id}", response_model=CustomerResponse)
def get_customer(customer_ref_or_id: str, db: Session = Depends(get_db)):
    """Get customer details by reference (e.g. CUST-000001) or primary key ID."""
    service = CustomerService(db)
    customer = service.get_customer_by_ref_or_id(customer_ref_or_id)

    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer with reference/ID '{customer_ref_or_id}' not found",
        )

    return CustomerResponse.model_validate(customer)
