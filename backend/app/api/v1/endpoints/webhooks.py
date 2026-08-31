"""
AI Chargeback Guardian — Payment Gateway & E-Commerce Webhook Ingestion
"""

import json
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.session import get_db
from app.models.entities import Customer, Transaction, Order, Delivery, Dispute, Evidence, AuditLog
from ml.service import ml_service

router = APIRouter()


class StripeDisputeWebhookPayload(BaseModel):
    id: str = Field(default="dp_simulated_stripe_001")
    object: str = "dispute"
    amount: float = 149.50
    currency: str = "USD"
    reason: str = "goods_not_received"
    status: str = "needs_response"
    customer_name: Optional[str] = "Jordan Hayes"
    customer_email: Optional[str] = "jordan.hayes@synthetic.test"
    merchant_id: Optional[int] = 1


@router.post("/stripe")
def ingest_stripe_dispute_webhook(
    payload: StripeDisputeWebhookPayload = Body(...),
    db: Session = Depends(get_db),
):
    """
    Ingest simulated Stripe `charge.dispute.created` webhook.
    Automatically provisions relational entities, runs XGBoost ML inference, and logs audit event.
    """
    try:
        now = datetime.utcnow()
        reason_map = {
            "goods_not_received": "GOODS_NOT_RECEIVED",
            "fraudulent": "UNAUTHORIZED_TRANSACTION",
            "duplicate": "DUPLICATE_TRANSACTION",
            "subscription_canceled": "REFUND_NOT_RECEIVED",
            "product_unacceptable": "GOODS_NOT_AS_DESCRIBED",
        }
        dispute_reason = reason_map.get(payload.reason.lower(), "GOODS_NOT_RECEIVED")

        ts_int = int(now.timestamp())

        # 1. Create synthetic customer
        customer = Customer(
            customer_reference=f"CUST-STRIPE-{ts_int % 100000}",
            account_age_days=180,
            previous_successful_transactions=6,
            previous_disputes=0,
            previous_refunds=0,
            customer_risk_history="LOW",
        )
        db.add(customer)
        db.flush()

        # 2. Create synthetic transaction
        tx = Transaction(
            transaction_reference=f"TXN-STRIPE-{ts_int % 100000}",
            customer_id=customer.id,
            merchant_id=payload.merchant_id or 1,
            amount=payload.amount,
            currency=payload.currency.upper(),
            transaction_timestamp=now,
            transaction_status="SUCCESS",
            payment_method_type="CREDIT_CARD",
            device_reference="DEV-STRIPE-001",
            location_region="US_EAST",
            transaction_frequency=1.0,
            amount_deviation=0.0,
        )
        db.add(tx)
        db.flush()

        # 3. Create synthetic order
        order = Order(
            order_reference=f"ORD-STRIPE-{ts_int % 100000}",
            transaction_id=tx.id,
            order_value=payload.amount,
            product_category="ELECTRONICS",
            order_timestamp=now,
            fulfillment_status="FULFILLED",
        )
        db.add(order)
        db.flush()

        # 4. Create synthetic delivery
        delivery = Delivery(
            order_id=order.id,
            delivery_status="DELIVERED",
            shipped_at=now,
            delivered_at=now,
            tracking_available=True,
            delivery_confirmed=True,
            customer_acknowledged=False,
        )
        db.add(delivery)
        db.flush()

        # 5. Create dispute record
        dispute_ref = f"DISP-STRIPE-{ts_int % 100000}"
        dispute = Dispute(
            dispute_reference=dispute_ref,
            transaction_id=tx.id,
            customer_id=customer.id,
            merchant_id=tx.merchant_id,
            dispute_reason=dispute_reason,
            dispute_amount=payload.amount,
            dispute_status="OPEN",
            dispute_timestamp=now,
        )
        db.add(dispute)
        db.flush()

        # 6. Create verified evidence records
        db.add(Evidence(
            dispute_id=dispute.id,
            evidence_type="PAYMENT",
            description="3D Secure 2.0 liability shift authenticated by cardholder bank",
            source_reference=f"STRIPE-CH-{tx.id}",
            available=True,
            verified=True,
            evidence_timestamp=now,
        ))
        db.add(Evidence(
            dispute_id=dispute.id,
            evidence_type="DELIVERY",
            description="FedEx delivery confirmation with GPS timestamp",
            source_reference=f"POD-FEDEX-{tx.id}",
            available=True,
            verified=True,
            evidence_timestamp=now,
        ))

        # 7. Log immutable audit trail
        db.add(AuditLog(
            dispute_id=dispute.id,
            action="DISPUTE_INGESTED_VIA_WEBHOOK",
            actor_type="SYSTEM",
            metadata_json=json.dumps({
                "gateway": "Stripe",
                "stripe_dispute_id": payload.id,
                "amount": payload.amount,
                "reason": dispute_reason,
            }),
            timestamp=now,
        ))
        db.commit()

        # 8. Run real-time ML risk assessment
        ml_prediction = ml_service.predict_single({
            "transaction_amount": payload.amount,
            "transaction_age": 1,
            "customer_account_age": 180,
            "previous_disputes": 0,
            "previous_successful_transactions": 6,
            "previous_refunds": 0,
            "evidence_count": 2,
            "merchant_dispute_rate": 0.01,
            "transaction_frequency": 1.2,
            "amount_deviation": 0.05,
            "delivery_confirmed": 1,
            "customer_acknowledged": 0,
            "refund_processed": 0,
            "communication_available": 0,
            "dispute_reason": dispute_reason,
            "payment_method": "CREDIT_CARD",
        })

        return {
            "status": "success",
            "message": "Stripe dispute successfully ingested and scored in real time",
            "dispute_id": dispute.id,
            "dispute_reference": dispute.dispute_reference,
            "amount": dispute.dispute_amount,
            "reason": dispute.dispute_reason,
            "ml_case_strength": ml_prediction.get("case_strength_score"),
            "ml_classification": ml_prediction.get("classification"),
            "investigation_url": f"/disputes/{dispute.id}",
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to ingest Stripe webhook: {str(e)}")
