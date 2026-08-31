"""
AI Chargeback Guardian — Multimodal OCR Endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.session import get_db
from app.services.ocr_service import OCRDocumentService

router = APIRouter()


class OCRUploadRequest(BaseModel):
    filename: str = Field(default="fedex_proof_of_delivery_gps.pdf")
    document_type: str = Field(default="COURIER_WAYBILL", description="COURIER_WAYBILL | BILLING_INVOICE | CUSTOMER_COMMUNICATION")
    raw_text: Optional[str] = None


@router.post("/{dispute_id}/upload-ocr")
def upload_ocr_document(
    dispute_id: int,
    payload: OCRUploadRequest = Body(...),
    db: Session = Depends(get_db),
):
    """
    Ingest and OCR-extract a simulated shipping waybill, tax invoice, or signed receipt.
    Attaches verified evidence directly to the dispute case.
    """
    try:
        service = OCRDocumentService(db)
        return service.extract_and_attach_document(
            dispute_id=dispute_id,
            filename=payload.filename,
            document_text_or_type=payload.document_type,
            raw_text=payload.raw_text,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
