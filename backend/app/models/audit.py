"""
AI Chargeback Guardian — Audit Trail ORM Model
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func

from app.database.base import Base


class AuditTrail(Base):
    """SQLAlchemy model for the audit trail table."""

    __tablename__ = "audit_trail"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dispute_id = Column(String(50), ForeignKey("disputes.dispute_id"), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    actor = Column(String(100), default="system")  # system, ai, human reviewer name
    timestamp = Column(DateTime, server_default=func.now())
