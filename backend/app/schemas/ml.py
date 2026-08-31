"""
AI Chargeback Guardian — ML Pydantic Schemas

Validates incoming feature payloads and structures ML prediction and metrics responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class MLPredictRequest(BaseModel):
    """Payload for real-time ML dispute risk scoring."""

    transaction_amount: float = Field(..., gt=0, description="Disputed transaction amount in USD")
    transaction_age: float = Field(..., ge=0, description="Days elapsed between transaction and dispute filing")
    customer_account_age: float = Field(..., ge=0, description="Customer account age in days")
    previous_disputes: int = Field(..., ge=0, description="Historical dispute count for customer")
    previous_successful_transactions: int = Field(..., ge=0, description="Historical successful order count")
    previous_refunds: int = Field(..., ge=0, description="Historical refund count for customer")
    evidence_count: int = Field(..., ge=0, le=7, description="Count of verified evidence categories (0-7)")
    merchant_dispute_rate: float = Field(..., ge=0.0, le=1.0, description="Merchant historical chargeback rate")
    transaction_frequency: float = Field(..., ge=0, description="Customer average transaction frequency")
    amount_deviation: float = Field(..., description="Z-score / normalized amount deviation")
    delivery_confirmed: int = Field(..., ge=0, le=1, description="1 if delivery confirmed by courier, else 0")
    customer_acknowledged: int = Field(..., ge=0, le=1, description="1 if customer acknowledged receipt, else 0")
    refund_processed: int = Field(..., ge=0, le=1, description="1 if refund was processed, else 0")
    communication_available: int = Field(..., ge=0, le=1, description="1 if pre-dispute support chat exists, else 0")
    dispute_reason: str = Field(..., description="Standard chargeback reason category")
    payment_method: str = Field(..., description="Payment method used for transaction")

    @field_validator("dispute_reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        valid_reasons = {
            "GOODS_NOT_RECEIVED",
            "UNAUTHORIZED_TRANSACTION",
            "GOODS_NOT_AS_DESCRIBED",
            "DUPLICATE_TRANSACTION",
            "REFUND_NOT_RECEIVED",
        }
        if v not in valid_reasons:
            raise ValueError(f"Invalid dispute_reason '{v}'. Must be one of: {sorted(valid_reasons)}")
        return v

    @field_validator("payment_method")
    @classmethod
    def validate_payment(cls, v: str) -> str:
        valid_methods = {
            "CREDIT_CARD",
            "DEBIT_CARD",
            "DIGITAL_WALLET",
            "BANK_TRANSFER",
        }
        if v not in valid_methods:
            raise ValueError(f"Invalid payment_method '{v}'. Must be one of: {sorted(valid_methods)}")
        return v


class SHAPFactor(BaseModel):
    """Local SHAP feature attribution element."""
    feature: str
    display_name: str
    contribution: float
    impact: str
    positive: bool


class MLPredictResponse(BaseModel):
    """Response returned from ML prediction endpoint."""

    case_strength_probability: float = Field(..., description="Probability of successfully contesting dispute (0.0 - 1.0)")
    case_strength_score: int = Field(..., description="Normalized Case Strength Score (0 - 100)")
    classification: str = Field(..., description="Case Strength Tier: WEAK, NEEDS_REVIEW, STRONG")
    recommend_contest: bool = Field(..., description="True if probability exceeds calibrated threshold")
    threshold: float = Field(..., description="Active decision threshold cutoff")
    model_version: str = Field(..., description="Trained model version identifier")
    model_name: str = Field(..., description="Model architecture name")
    top_positive_factors: List[SHAPFactor] = Field(default_factory=list, description="Top positive contributing factors")
    top_negative_factors: List[SHAPFactor] = Field(default_factory=list, description="Top negative contributing factors")
    disclaimer: str = Field(..., description="Legal and regulatory compliance notice")


class ConfusionMatrixStats(BaseModel):
    true_negatives: int
    false_positives: int
    false_negatives: int
    true_positives: int


class ModelEvaluationMetrics(BaseModel):
    model_name: str
    threshold: float
    total_samples: int
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float
    pr_auc: float
    false_positive_rate: float
    false_negative_rate: float
    confusion_matrix: ConfusionMatrixStats


class ThresholdSweepRow(BaseModel):
    threshold: float
    precision: float
    recall: float
    f1_score: float
    false_positive_rate: float
    false_negative_rate: float
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    fp_cost_total: float
    fn_cost_total: float
    total_expected_cost: float
    avg_cost_per_case: float


class GlobalFeatureImportance(BaseModel):
    feature: str
    importance: float


class MLMetricsResponse(BaseModel):
    """Comprehensive model evaluation benchmark response."""

    model_version: str
    model_name: str
    baseline_model_name: str
    threshold: float
    score_tiers: Dict[str, int]
    business_costs: Dict[str, float]
    test_metrics: ModelEvaluationMetrics
    baseline_metrics: ModelEvaluationMetrics
    threshold_analysis: List[ThresholdSweepRow]
    top_global_features: List[GlobalFeatureImportance]
    legal_disclaimer: str
