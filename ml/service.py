"""
AI Chargeback Guardian — ML Prediction Service

Provides a clean, unified prediction interface:
1. Loads serialized champion model and ColumnTransformer preprocessor
2. Validates incoming dispute/transaction feature dictionaries
3. Computes automated feature engineering
4. Generates win probability, 0–100 Case Strength Score, and tier classification:
   - 0–39: WEAK
   - 40–69: NEEDS_REVIEW
   - 70–100: STRONG
5. Extracts local SHAP contributing factors (top positive & negative drivers)
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd

from ml.config import (
    SAVED_MODELS_DIR,
    BASE_FEATURES,
    NUMERIC_FEATURES,
    BINARY_FEATURES,
    CATEGORICAL_FEATURES,
    DEFAULT_CONTEST_THRESHOLD,
    SCORE_WEAK_MAX,
    SCORE_REVIEW_MAX,
    SCORE_STRONG_MIN,
    MODEL_VERSION,
)
from ml.preprocessing.pipeline import engineer_features
from ml.explainability.shap_explainer import (
    init_shap_explainer,
    explain_prediction,
    LEGAL_DISCLAIMER,
)


class MLPredictionService:
    """Singleton-style or on-demand ML Prediction Service."""

    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = models_dir or SAVED_MODELS_DIR
        self.model: Optional[Any] = None
        self.preprocessor: Optional[Any] = None
        self.explainer: Optional[Any] = None
        self.metadata: Dict[str, Any] = {}
        self.is_loaded = False
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        """Load trained model, preprocessor, and metadata from disk."""
        model_path = self.models_dir / "chargeback_model.joblib"
        preprocessor_path = self.models_dir / "preprocessor.joblib"
        metadata_path = self.models_dir / "model_metadata.json"

        if not model_path.exists() or not preprocessor_path.exists():
            # Artifacts not yet trained; leave unloaded
            self.is_loaded = False
            return

        try:
            self.model = joblib.load(model_path)
            self.preprocessor = joblib.load(preprocessor_path)

            if metadata_path.exists():
                with open(metadata_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)

            # Initialize SHAP explainer
            self.explainer = init_shap_explainer(self.model)
            self.is_loaded = True
        except Exception as e:
            self.is_loaded = False
            print(f"[MLPredictionService] Warning loading artifacts: {e}")

    def predict_single(self, feature_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run inference on a single dispute/transaction feature dictionary.

        Parameters
        ----------
        feature_data : dict containing all base features:
            - transaction_amount (float)
            - transaction_age (int/float)
            - customer_account_age (int/float)
            - previous_disputes (int)
            - previous_successful_transactions (int)
            - previous_refunds (int)
            - evidence_count (int, 0 to 7)
            - merchant_dispute_rate (float, 0.0 to 1.0)
            - transaction_frequency (float)
            - amount_deviation (float)
            - delivery_confirmed (int/bool)
            - customer_acknowledged (int/bool)
            - refund_processed (int/bool)
            - communication_available (int/bool)
            - dispute_reason (str)
            - payment_method (str)

        Returns
        -------
        dict
            Inference response containing win probability, case strength score,
            classification tier, decision threshold, top SHAP factors, and disclaimer.
        """
        if not self.is_loaded:
            # Re-attempt loading in case models were trained recently
            self._load_artifacts()

        if not self.is_loaded or self.model is None or self.preprocessor is None:
            raise RuntimeError(
                "ML model is not available. Please run `python ml/train.py` to train and serialize the model."
            )

        # Validate required keys
        missing = [f for f in BASE_FEATURES if f not in feature_data]
        if missing:
            raise ValueError(f"Missing required feature fields: {missing}")

        # Convert to single-row DataFrame
        df_input = pd.DataFrame([feature_data])

        # Feature engineering
        df_engineered = engineer_features(df_input)

        # ColumnTransformer transform
        X_trans = self.preprocessor.transform(df_engineered)

        # Predict probability
        proba = float(self.model.predict_proba(X_trans)[0, 1])
        score = int(round(proba * 100))

        # Classification tier
        threshold = float(self.metadata.get("threshold", DEFAULT_CONTEST_THRESHOLD))
        if score >= SCORE_STRONG_MIN:
            classification = "STRONG"
        elif score >= (SCORE_WEAK_MAX + 1):
            classification = "NEEDS_REVIEW"
        else:
            classification = "WEAK"

        recommend_contest = bool(proba >= threshold)

        # Generate SHAP explanation
        explanation = explain_prediction(
            self.explainer,
            self.model,
            X_trans,
            feature_names=self.preprocessor.get_feature_names_out(),
            top_k=4,
        )

        return {
            "case_strength_probability": round(proba, 4),
            "case_strength_score": score,
            "classification": classification,
            "recommend_contest": recommend_contest,
            "threshold": threshold,
            "model_version": self.metadata.get("model_version", MODEL_VERSION),
            "model_name": self.metadata.get("model_name", "xgboost"),
            "top_positive_factors": explanation["top_positive_factors"],
            "top_negative_factors": explanation["top_negative_factors"],
            "disclaimer": LEGAL_DISCLAIMER,
        }


# Global singleton instance
ml_service = MLPredictionService()
