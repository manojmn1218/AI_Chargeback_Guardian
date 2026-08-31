"""
AI Chargeback Guardian — Explainability Service (Step 6)

Provides local TreeSHAP feature attributions for individual dispute cases:
- Computes genuine feature contributions directly from the trained tree model.
- Maps raw engineered features to clean, human-readable operational terms.
- Strictly uses non-causal terminology ("contributing factor" rather than "caused").
- Provides a graceful, clearly-labeled fallback if SHAP is uninitialized.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.models import Dispute, Delivery, Refund, Communication, Evidence
from app.services.ml_service import BackendMLService
from app.schemas.explainability import SHAPFeatureContribution, DisputeExplanationResponse
from ml.service import ml_service
from ml.preprocessing.pipeline import engineer_features
from ml.explainability.shap_explainer import explain_prediction, LEGAL_DISCLAIMER, SHAP_AVAILABLE


class ExplainabilityService:
    """Service layer for computing and formatting local model explainability."""

    def __init__(self, db: Session):
        self.db = db
        self.backend_ml = BackendMLService(db)

    def get_explanation(self, dispute_ref_or_id: str) -> DisputeExplanationResponse:
        """
        Generate local TreeSHAP explanation for a specific dispute.
        """
        # 1. Fetch Dispute record
        if str(dispute_ref_or_id).isdigit():
            dispute = self.db.query(Dispute).filter(Dispute.id == int(dispute_ref_or_id)).first()
        else:
            dispute = self.db.query(Dispute).filter(Dispute.dispute_reference == str(dispute_ref_or_id)).first()

        if not dispute:
            raise ValueError(f"Dispute '{dispute_ref_or_id}' not found.")

        txn = dispute.transaction
        cust = dispute.customer
        merch = dispute.merchant
        ord_rec = txn.order if txn else None
        deliv = self.db.query(Delivery).filter(Delivery.order_id == ord_rec.id).first() if ord_rec else None

        if not txn or not cust or not merch:
            raise ValueError(f"Incomplete relational entity records for dispute '{dispute_ref_or_id}'.")

        # 2. Extract base features
        ev_count = self.db.query(Evidence).filter(
            Evidence.dispute_id == dispute.id,
            Evidence.available == True,
        ).count()
        refund_proc = 1 if self.db.query(Refund).filter(Refund.transaction_id == txn.id).first() else 0
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

        # 3. Transform through ML pipeline
        df_input = pd.DataFrame([feature_dict])
        df_engineered = engineer_features(df_input)

        if not ml_service.is_loaded:
            ml_service._load_artifacts()

        if not ml_service.is_loaded or ml_service.model is None or ml_service.preprocessor is None:
            raise RuntimeError("ML Model artifacts are not loaded.")

        X_trans = ml_service.preprocessor.transform(df_engineered)
        feature_names = ml_service.preprocessor.get_feature_names_out()

        # 4. Generate SHAP or Fallback explanation
        method = "SHAP" if (ml_service.explainer is not None and SHAP_AVAILABLE) else "MODEL_FEATURE_IMPORTANCE_FALLBACK"

        shap_res = explain_prediction(
            ml_service.explainer,
            ml_service.model,
            X_trans,
            feature_names=feature_names,
            top_k=5,
        )

        proba = shap_res["case_strength_probability"]
        score = int(round(proba * 100))
        base_val = shap_res.get("base_value", 0.50)

        if score >= 70:
            classification = "STRONG"
        elif score >= 40:
            classification = "NEEDS_REVIEW"
        else:
            classification = "WEAK"

        # Build feature attribution list
        all_features: List[SHAPFeatureContribution] = []
        for item in shap_res.get("all_factors", []):
            feat_name = item["feature"]
            val_raw = None
            # Extract raw value if in engineered dataframe
            clean_feat = feat_name.replace("num__", "").replace("bin__", "").replace("cat__", "").replace("remainder__", "")
            if clean_feat in df_engineered.columns:
                val_raw = df_engineered[clean_feat].values[0]
                if isinstance(val_raw, (np.floating, float)):
                    val_raw = round(float(val_raw), 2)
                elif isinstance(val_raw, (np.integer, int)):
                    val_raw = int(val_raw)

            all_features.append(
                SHAPFeatureContribution(
                    feature=feat_name,
                    display_name=item["display_name"],
                    value=val_raw,
                    contribution=item["contribution"],
                    direction="positive" if item["positive"] else "negative",
                    impact_pct=item["impact"],
                )
            )

        pos_factors = [
            SHAPFeatureContribution(
                feature=f["feature"],
                display_name=f["display_name"],
                value=None,
                contribution=f["contribution"],
                direction="positive",
                impact_pct=f["impact"],
            )
            for f in shap_res.get("top_positive_factors", [])
        ]

        neg_factors = [
            SHAPFeatureContribution(
                feature=f["feature"],
                display_name=f["display_name"],
                value=None,
                contribution=f["contribution"],
                direction="negative",
                impact_pct=f["impact"],
            )
            for f in shap_res.get("top_negative_factors", [])
        ]

        return DisputeExplanationResponse(
            dispute_id=str(dispute.id),
            dispute_reference=dispute.dispute_reference,
            model_version=ml_service.metadata.get("model_version", "v1.0"),
            model_name=ml_service.metadata.get("model_name", "xgboost"),
            score=score,
            classification=classification,
            prediction_probability=proba,
            base_value=base_val,
            features=all_features,
            top_positive_factors=pos_factors,
            top_negative_factors=neg_factors,
            method=method,
            disclaimer=LEGAL_DISCLAIMER,
        )
