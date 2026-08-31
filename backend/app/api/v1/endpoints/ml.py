"""
AI Chargeback Guardian — ML Prediction & Metrics Endpoints (Step 3)

Provides:
- POST /api/v1/ml/predict: Real-time dispute case strength estimation and SHAP attribution.
- GET /api/v1/ml/metrics: Comprehensive held-out evaluation benchmarks, baseline comparison,
  and threshold cost curve.
- GET /api/v1/ml/score-dispute/{id}: Automated relational feature scoring for stored disputes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, Dict

from app.database.session import get_db
from app.services.ml_service import BackendMLService
from app.schemas.ml import (
    MLPredictRequest,
    MLPredictResponse,
    MLMetricsResponse,
)

router = APIRouter()


@router.post(
    "/predict",
    response_model=MLPredictResponse,
    status_code=status.HTTP_200_OK,
    summary="Estimate Chargeback Case Strength & SHAP Attribution",
)
def predict_chargeback_strength(
    request: MLPredictRequest,
):
    """
    Run the ML Risk Engine (XGBoost) on validated dispute features.

    Returns:
    - case_strength_probability: Probability (0.0 to 1.0) of winning contest
    - case_strength_score: Normalized 0 to 100 score
    - classification: Case tier (WEAK, NEEDS_REVIEW, STRONG)
    - recommend_contest: Binary recommendation based on optimal decision threshold (tau=0.60)
    - top_positive_factors & top_negative_factors: Local SHAP attribution waterfall drivers
    - disclaimer: Legal compliance notice
    """
    try:
        service = BackendMLService()
        result = service.predict_from_payload(request.model_dump())
        return MLPredictResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}",
        )


@router.get(
    "/metrics",
    response_model=MLMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Stored Model Performance Benchmarks",
)
def get_model_metrics():
    """
    Retrieve real held-out test evaluation benchmarks from model_metadata.json:
    - XGBoost Champion vs Logistic Regression Baseline comparison
    - Precision, Recall, F1, ROC-AUC, PR-AUC, Confusion Matrix breakdown
    - Multi-threshold sweep (0.10 to 0.90) with asymmetric financial cost analysis ($15 FP vs $489 FN)
    - Global feature importance ranking
    """
    try:
        service = BackendMLService()
        metrics = service.get_stored_metrics()
        return MLMetricsResponse(**metrics)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model metrics have not been generated yet. Please execute training script.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read model metrics: {str(e)}",
        )


@router.get(
    "/score-dispute/{dispute_id_or_ref}",
    response_model=MLPredictResponse,
    status_code=status.HTTP_200_OK,
    summary="Score Stored Dispute Record by ID or Reference",
)
def score_dispute_record(
    dispute_id_or_ref: str,
    db: Session = Depends(get_db),
):
    """
    Extract relational entities for a database dispute and compute ML contest strength score.
    """
    try:
        service = BackendMLService(db)
        result = service.score_dispute_by_id(dispute_id_or_ref)
        return MLPredictResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
