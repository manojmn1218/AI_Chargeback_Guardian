"""
AI Chargeback Guardian — Export & Document Packet Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.pdf_packet_service import EvidencePacketService

router = APIRouter()


@router.get("/{dispute_id}/packet", response_class=HTMLResponse)
def export_evidence_packet(
    dispute_id: str,
    reviewer: str = Query("Alex Vance", description="Reviewer name for certification"),
    db: Session = Depends(get_db),
):
    """
    Generate an official Visa/Mastercard Compelling Evidence 3.0 formal rebuttal packet.
    Formatted for direct browser printing or saving as PDF.
    """
    try:
        service = EvidencePacketService(db)
        html_content = service.generate_html_packet(dispute_id, reviewer_name=reviewer)
        return HTMLResponse(content=html_content, status_code=200)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate evidence packet: {str(e)}")
