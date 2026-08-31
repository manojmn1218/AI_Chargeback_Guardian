"""
AI Chargeback Guardian — Pydantic Schemas for All Entities (Step 2)
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


# ----------------- Customer -----------------
class CustomerBase(BaseModel):
    customer_reference: str
    account_age_days: int
    previous_successful_transactions: int
    previous_disputes: int
    previous_refunds: int
    customer_risk_history: str


class CustomerResponse(CustomerBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CustomerListResponse(BaseModel):
    items: List[CustomerResponse]
    total: int
    page: int
    page_size: int


# ----------------- Merchant -----------------
class MerchantBase(BaseModel):
    merchant_reference: str
    merchant_category: str
    account_age_days: int
    historical_dispute_rate: float
    historical_success_rate: float


class MerchantResponse(MerchantBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MerchantListResponse(BaseModel):
    items: List[MerchantResponse]
    total: int
    page: int
    page_size: int


# ----------------- Transaction -----------------
class TransactionBase(BaseModel):
    transaction_reference: str
    customer_id: int
    merchant_id: int
    amount: float
    currency: str = "USD"
    transaction_timestamp: datetime
    transaction_status: str
    payment_method_type: str
    device_reference: str
    location_region: str
    transaction_frequency: float
    amount_deviation: float


class TransactionResponse(TransactionBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TransactionListResponse(BaseModel):
    items: List[TransactionResponse]
    total: int
    page: int
    page_size: int


# ----------------- Order & Delivery -----------------
class DeliveryResponse(BaseModel):
    id: int
    order_id: int
    delivery_status: str
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    tracking_available: bool
    delivery_confirmed: bool
    customer_acknowledged: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    order_reference: str
    transaction_id: int
    order_value: float
    product_category: str
    order_timestamp: datetime
    fulfillment_status: str
    delivery: Optional[DeliveryResponse] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ----------------- Refund -----------------
class RefundResponse(BaseModel):
    id: int
    transaction_id: int
    refund_status: str
    refund_amount: float
    refund_timestamp: datetime
    refund_reason: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ----------------- Evidence -----------------
class EvidenceResponse(BaseModel):
    id: int
    dispute_id: int
    evidence_type: str
    description: str
    source_reference: str
    available: bool
    verified: bool
    evidence_timestamp: datetime
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DisputeEvidenceListResponse(BaseModel):
    dispute_reference: str
    items: List[EvidenceResponse]
    total_available: int
    total_categories: int
    completeness_percentage: float


# ----------------- Communication -----------------
class CommunicationResponse(BaseModel):
    id: int
    dispute_id: int
    communication_type: str
    communication_timestamp: datetime
    verified: bool
    content_summary: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ----------------- Dispute -----------------
class DisputeBase(BaseModel):
    dispute_reference: str
    transaction_id: int
    customer_id: int
    merchant_id: int
    dispute_reason: str
    dispute_amount: float
    dispute_status: str
    dispute_timestamp: datetime
    outcome: Optional[int] = None


class DisputeResponse(DisputeBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DisputeDetailResponse(DisputeResponse):
    customer: Optional[CustomerResponse] = None
    merchant: Optional[MerchantResponse] = None
    transaction: Optional[TransactionResponse] = None
    evidence_items: List[EvidenceResponse] = []
    communications: List[CommunicationResponse] = []

    model_config = ConfigDict(from_attributes=True)


class DisputeListResponse(BaseModel):
    items: List[DisputeResponse]
    total: int
    page: int
    page_size: int
