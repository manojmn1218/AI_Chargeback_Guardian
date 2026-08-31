"""
AI Chargeback Guardian — Dispute ORM Model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func

from app.database.base import Base


class Dispute(Base):
    """SQLAlchemy model for the disputes table."""

    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dispute_id = Column(String(50), unique=True, nullable=False, index=True)
    transaction_id = Column(String(50), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    reason = Column(String(100), nullable=False)
    reason_code = Column(String(20), nullable=True)
    status = Column(String(30), default="open")  # open, under_review, resolved, closed
    risk_level = Column(String(20), nullable=True)  # high, medium, low
    risk_score = Column(Float, nullable=True)

    # Customer info
    customer_name = Column(String(100), nullable=True)
    customer_email = Column(String(150), nullable=True)

    # Merchant info
    merchant_name = Column(String(100), nullable=True)
    merchant_id = Column(String(50), nullable=True)

    # Investigation
    recommendation = Column(String(30), nullable=True)  # contest, accept, review
    ai_response_draft = Column(Text, nullable=True)
    final_response = Column(Text, nullable=True)
    reviewer_decision = Column(String(30), nullable=True)  # approved, rejected, edited
    reviewer_notes = Column(Text, nullable=True)

    # Timestamps
    transaction_date = Column(DateTime, nullable=True)
    dispute_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
