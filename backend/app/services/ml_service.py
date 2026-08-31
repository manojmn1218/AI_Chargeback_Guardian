"""
AI Chargeback Guardian — Backend ML Service Adapter

Bridges FastAPI endpoints and database dispute records with the ML prediction engine:
- Live inference from raw feature JSON payloads
- Direct inference from SQLite dispute IDs with automatic relational feature extraction
- Access to stored model performance benchmarks and metadata
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
import json
from sqlalchemy.orm import Session

import sys
from pathlib import Path

# Add project root to sys.path so ml package is importable
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ml.service import ml_service, MLPredictionService
from ml.config import SAVED_MODELS_DIR
from app.models import Dispute, Transaction, Customer, Merchant, Delivery, Evidence, Refund, Communication, Order


class BackendMLService:
    """Service layer for ML scoring and evaluation metrics retrieval."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.ml_engine = ml_service

    def predict_from_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run ML risk scoring on user-provided feature payload."""
        return self.ml_engine.predict_single(payload)

    def score_dispute_by_id(self, dispute_id_or_ref: str) -> Dict[str, Any]:
        """
        Extract relational features for a database dispute and compute ML prediction.

        Parameters
        ----------
        dispute_id_or_ref : str
            Dispute ID (int as str) or dispute_reference (e.g. 'DISP-000001').
        """
        if not self.db:
            raise RuntimeError("Database session required for dispute ID lookup.")

        # Query dispute
        if dispute_id_or_ref.isdigit():
            dispute = self.db.query(Dispute).filter(Dispute.id == int(dispute_id_or_ref)).first()
        else:
            dispute = self.db.query(Dispute).filter(Dispute.dispute_reference == dispute_id_or_ref).first()

        if not dispute:
            raise ValueError(f"Dispute '{dispute_id_or_ref}' not found in database.")

        txn = dispute.transaction
        cust = dispute.customer
        merch = dispute.merchant
        ord_rec = txn.order if txn else None
        deliv = self.db.query(Delivery).filter(Delivery.order_id == ord_rec.id).first() if ord_rec else None

        if not txn or not cust or not merch:
            raise ValueError(f"Incomplete relational entity records for dispute '{dispute_id_or_ref}'.")

        # Aggregate evidence count
        ev_count = self.db.query(Evidence).filter(
            Evidence.dispute_id == dispute.id,
            Evidence.available == True,
        ).count()

        # Check refund
        refund_proc = 1 if self.db.query(Refund).filter(Refund.transaction_id == txn.id).first() else 0

        # Check communications
        comm_avail = 1 if self.db.query(Communication).filter(Communication.dispute_id == dispute.id).first() else 0

        txn_age = max(1, (dispute.dispute_timestamp - txn.transaction_timestamp).days)

        feature_dict = {
            "transaction_amount": float(txn.amount),
            "transaction_age": txn_age,
            "customer_account_age": int(cust.account_age_days),
            "previous_disputes": int(cust.previous_disputes),
            "previous_successful_transactions": int(cust.previous_successful_transactions),
            "previous_refunds": int(cust.previous_refunds),
            "evidence_count": ev_count,
            "merchant_dispute_rate": float(merch.historical_dispute_rate),
            "transaction_frequency": float(txn.transaction_frequency),
            "amount_deviation": float(txn.amount_deviation),
            "delivery_confirmed": 1 if (deliv and deliv.delivery_confirmed) else 0,
            "customer_acknowledged": 1 if (deliv and deliv.customer_acknowledged) else 0,
            "refund_processed": refund_proc,
            "communication_available": comm_avail,
            "dispute_reason": str(dispute.dispute_reason),
            "payment_method": str(txn.payment_method_type),
        }

        result = self.ml_engine.predict_single(feature_dict)
        result["dispute_id"] = dispute.id
        result["dispute_reference"] = dispute.dispute_reference
        return result

    def get_stored_metrics(self) -> Dict[str, Any]:
        """Read and return stored evaluation benchmark results from disk."""
        metrics_file = SAVED_MODELS_DIR / "metrics.json"
        metadata_file = SAVED_MODELS_DIR / "model_metadata.json"

        if not metrics_file.exists() or not metadata_file.exists():
            raise FileNotFoundError("Model performance metrics not found. Run `python ml/train.py` first.")

        with open(metrics_file, "r", encoding="utf-8") as f:
            metrics_data = json.load(f)

        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata_data = json.load(f)

        return {
            "model_version": metadata_data.get("model_version", "v1.0"),
            "model_name": metadata_data.get("model_name", "xgboost"),
            "baseline_model_name": metadata_data.get("baseline_model_name", "logistic_regression"),
            "threshold": metadata_data.get("threshold", 0.60),
            "score_tiers": metadata_data.get("score_tiers", {}),
            "business_costs": metadata_data.get("business_costs", {}),
            "test_metrics": metrics_data.get("champion", {}),
            "baseline_metrics": metrics_data.get("baseline", {}),
            "threshold_analysis": metrics_data.get("threshold_analysis", []),
            "top_global_features": metrics_data.get("global_features", []),
            "legal_disclaimer": metadata_data.get("legal_disclaimer", ""),
        }
