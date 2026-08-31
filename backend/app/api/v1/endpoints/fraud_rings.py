"""
AI Chargeback Guardian — Fraud Ring & Entity Linking Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.fraud_ring_service import FraudRingService

router = APIRouter()


@router.get("/graph")
def get_fraud_ring_graph(db: Session = Depends(get_db)):
    """
    Retrieve interactive entity-linking graph data showing multi-account device & card syndicates.
    """
    try:
        service = FraudRingService(db)
        return service.get_fraud_rings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate fraud ring graph: {str(e)}")
