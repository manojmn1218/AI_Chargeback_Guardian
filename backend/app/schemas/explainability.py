"""
AI Chargeback Guardian — Explainability Pydantic Schemas (Step 6)

Defines data contracts for SHAP local waterfall feature attributions,
direction classification, contributing factor rankings, and model methodology disclosures.
"""

from typing import List, Optional, Any, Literal, Dict
from pydantic import BaseModel, Field


class SHAPFeatureContribution(BaseModel):
    """Granular feature attribution for a dispute prediction."""
    feature: str = Field(..., description="Raw model feature identifier")
    display_name: str = Field(..., description="Human-readable business feature label")
    value: Optional[Any] = Field(default=None, description="Actual dispute feature value")
    contribution: float = Field(..., description="SHAP attribution value (log-odds / probability impact)")
    direction: Literal["positive", "negative"] = Field(..., description="Direction of impact on contest win probability")
    impact_pct: str = Field(..., description="Formatted percentage impact representation (+X.X% / -X.X%)")


class DisputeExplanationResponse(BaseModel):
    """Complete explainability payload returned by GET /api/v1/disputes/{id}/explanation."""
    dispute_id: str
    dispute_reference: str
    model_version: str
    model_name: str
    score: int = Field(..., description="Normalized Case Strength Score (0 - 100)")
    classification: str = Field(..., description="WEAK, NEEDS_REVIEW, STRONG")
    prediction_probability: float = Field(..., description="Exact win probability (0.0 - 1.0)")
    base_value: float = Field(..., description="Expected baseline model probability across population")
    features: List[SHAPFeatureContribution] = Field(default_factory=list, description="All evaluated feature attributions")
    top_positive_factors: List[SHAPFeatureContribution] = Field(default_factory=list, description="Top positive win probability drivers")
    top_negative_factors: List[SHAPFeatureContribution] = Field(default_factory=list, description="Top risk / vulnerability drivers")
    method: str = Field(default="SHAP", description="SHAP | MODEL_FEATURE_IMPORTANCE_FALLBACK")
    disclaimer: str = Field(
        default="Model explanations represent mathematical contributing factors within the predictive model and do NOT constitute guaranteed legal causation under card network arbitration rules."
    )
