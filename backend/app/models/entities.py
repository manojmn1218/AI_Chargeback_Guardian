"""
AI Chargeback Guardian — Comprehensive Relational ORM Models (Step 2)
All models support realistic synthetic chargeback investigation workflows.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Customer(Base):
    """Synthetic customer entity — strictly no personal identifying information."""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_reference = Column(String(50), unique=True, nullable=False, index=True)  # e.g., CUST-000001
    account_age_days = Column(Integer, nullable=False, default=30)
    previous_successful_transactions = Column(Integer, nullable=False, default=0)
    previous_disputes = Column(Integer, nullable=False, default=0)
    previous_refunds = Column(Integer, nullable=False, default=0)
    customer_risk_history = Column(String(20), nullable=False, default="LOW")  # LOW, MEDIUM, HIGH
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    transactions = relationship("Transaction", back_populates="customer")
    disputes = relationship("Dispute", back_populates="customer")


class Merchant(Base):
    """Synthetic merchant entity."""
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    merchant_reference = Column(String(50), unique=True, nullable=False, index=True)  # e.g., MER-000001
    merchant_category = Column(String(100), nullable=False)  # e.g., RETAIL, ELECTRONICS, DIGITAL, SUBSCRIPTION
    account_age_days = Column(Integer, nullable=False, default=180)
    historical_dispute_rate = Column(Float, nullable=False, default=0.01)
    historical_success_rate = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    transactions = relationship("Transaction", back_populates="merchant")
    disputes = relationship("Dispute", back_populates="merchant")
    policies = relationship("MerchantPolicy", back_populates="merchant")


class Transaction(Base):
    """Synthetic transaction record."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_reference = Column(String(50), unique=True, nullable=False, index=True)  # e.g., TXN-000001
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    transaction_timestamp = Column(DateTime, nullable=False)
    transaction_status = Column(String(30), default="SUCCESS", nullable=False)  # SUCCESS, FAILED, PENDING
    payment_method_type = Column(String(50), nullable=False)  # CREDIT_CARD, DEBIT_CARD, DIGITAL_WALLET, BANK_TRANSFER
    device_reference = Column(String(50), nullable=False)  # e.g., DEV-000123
    location_region = Column(String(50), nullable=False)  # e.g., US_EAST, US_WEST, EU_CENTRAL, APAC_SOUTH
    transaction_frequency = Column(Float, nullable=False, default=1.0)
    amount_deviation = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="transactions")
    merchant = relationship("Merchant", back_populates="transactions")
    order = relationship("Order", back_populates="transaction", uselist=False)
    refunds = relationship("Refund", back_populates="transaction")
    dispute = relationship("Dispute", back_populates="transaction", uselist=False)


class Order(Base):
    """Synthetic order linked to a transaction."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_reference = Column(String(50), unique=True, nullable=False, index=True)  # e.g., ORD-000001
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, unique=True, index=True)
    order_value = Column(Float, nullable=False)
    product_category = Column(String(100), nullable=False)  # ELECTRONICS, DIGITAL_GOODS, APPAREL, SERVICES, HOME
    order_timestamp = Column(DateTime, nullable=False)
    fulfillment_status = Column(String(30), default="FULFILLED", nullable=False)  # FULFILLED, PENDING, CANCELLED
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    transaction = relationship("Transaction", back_populates="order")
    delivery = relationship("Delivery", back_populates="order", uselist=False)


class Delivery(Base):
    """Synthetic delivery status for orders."""
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True, index=True)
    delivery_status = Column(String(30), default="DELIVERED", nullable=False)  # DELIVERED, IN_TRANSIT, FAILED, RETURNED
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    tracking_available = Column(Boolean, default=True, nullable=False)
    delivery_confirmed = Column(Boolean, default=True, nullable=False)
    customer_acknowledged = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="delivery")


class Refund(Base):
    """Synthetic refund record linked to a transaction."""
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, index=True)
    refund_status = Column(String(30), default="PROCESSED", nullable=False)  # PROCESSED, REJECTED, PENDING
    refund_amount = Column(Float, nullable=False)
    refund_timestamp = Column(DateTime, nullable=False)
    refund_reason = Column(String(200), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    transaction = relationship("Transaction", back_populates="refunds")


class Dispute(Base):
    """Synthetic dispute record representing a payment chargeback."""
    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dispute_reference = Column(String(50), unique=True, nullable=False, index=True)  # e.g., DISP-000001
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, unique=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, index=True)
    dispute_reason = Column(String(100), nullable=False)
    # Reasons: GOODS_NOT_RECEIVED, GOODS_NOT_AS_DESCRIBED, DUPLICATE_TRANSACTION, UNAUTHORIZED_TRANSACTION, REFUND_NOT_RECEIVED
    dispute_amount = Column(Float, nullable=False)
    dispute_status = Column(String(30), default="OPEN", nullable=False)  # OPEN, UNDER_REVIEW, RESOLVED, CLOSED
    dispute_timestamp = Column(DateTime, nullable=False)
    outcome = Column(Integer, nullable=True)  # 1 = Merchant Win (Contest Success), 0 = Merchant Lost (Fraud/Valid Claim)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    transaction = relationship("Transaction", back_populates="dispute")
    customer = relationship("Customer", back_populates="disputes")
    merchant = relationship("Merchant", back_populates="disputes")
    evidence_items = relationship("Evidence", back_populates="dispute", cascade="all, delete-orphan")
    communications = relationship("Communication", back_populates="dispute", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="dispute", cascade="all, delete-orphan")
    human_reviews = relationship("HumanReview", back_populates="dispute", cascade="all, delete-orphan")



class Evidence(Base):
    """Evidence category items attached to a dispute case."""
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dispute_id = Column(Integer, ForeignKey("disputes.id"), nullable=False, index=True)
    evidence_type = Column(String(50), nullable=False)
    # Types: PAYMENT, INVOICE, ORDER, DELIVERY, REFUND, CUSTOMER_COMMUNICATION, MERCHANT_POLICY
    description = Column(Text, nullable=False)
    source_reference = Column(String(100), nullable=False)  # e.g., GATEWAY_3DS_AUTH, COURIER_GPS_LOG
    available = Column(Boolean, default=True, nullable=False)
    verified = Column(Boolean, default=True, nullable=False)
    evidence_timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    dispute = relationship("Dispute", back_populates="evidence_items")


class Communication(Base):
    """Customer-merchant communication logs linked to a dispute."""
    __tablename__ = "communications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dispute_id = Column(Integer, ForeignKey("disputes.id"), nullable=False, index=True)
    communication_type = Column(String(50), nullable=False)  # SUPPORT_CHAT, EMAIL, PHONE_LOG, SMS
    communication_timestamp = Column(DateTime, nullable=False)
    verified = Column(Boolean, default=True, nullable=False)
    content_summary = Column(Text, nullable=False)  # Synthetic summary, no personal info
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    dispute = relationship("Dispute", back_populates="communications")


class MerchantPolicy(Base):
    """Merchant policies (e.g. Terms of Service, Refund Policy)."""
    __tablename__ = "merchant_policies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, index=True)
    policy_type = Column(String(50), nullable=False)  # TERMS_OF_SERVICE, REFUND_POLICY, SHIPPING_POLICY, CANCELLATION_POLICY
    policy_text = Column(Text, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    merchant = relationship("Merchant", back_populates="policies")


class AuditLog(Base):
    """Immutable audit trail for dispute investigation actions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dispute_id = Column(Integer, ForeignKey("disputes.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    actor_type = Column(String(30), nullable=False)  # SYSTEM, AI, HUMAN
    metadata_json = Column(Text, nullable=True)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    dispute = relationship("Dispute", back_populates="audit_logs")


class HumanReview(Base):
    """Human-in-the-loop dispute review decision record."""
    __tablename__ = "human_reviews"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dispute_id = Column(Integer, ForeignKey("disputes.id"), nullable=False, index=True)
    reviewer_reference = Column(String(50), nullable=False, default="REV-00892")  # Synthetic reviewer ID
    original_ai_recommendation = Column(String(50), nullable=False)  # CONTEST, REVIEW, ACCEPT
    original_ai_response = Column(Text, nullable=False)
    reviewer_decision = Column(String(50), nullable=False)  # APPROVE, REJECT, EDIT_AND_APPROVE, NEEDS_MORE_EVIDENCE
    edited_response = Column(Text, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, server_default=func.now(), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    dispute = relationship("Dispute", back_populates="human_reviews")

