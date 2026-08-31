"""
AI Chargeback Guardian — Analytics Pydantic Schemas (Step 7)
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class RecommendationDistribution(BaseModel):
    CONTEST: int = 0
    REVIEW: int = 0
    ACCEPT: int = 0


class AnalyticsOverviewResponse(BaseModel):
    """Calculated operational summary metrics."""
    total_disputes: int
    open_disputes: int
    pending_reviews: int
    approved: int
    rejected: int
    recommended_contest: int
    high_risk: int
    average_case_strength: float
    average_evidence_completeness: float
    total_amount_at_risk: float
    recommendation_distribution: Dict[str, int]


class TimeSeriesTrendItem(BaseModel):
    period: str
    count: int
    total_amount: float


class DistributionBucket(BaseModel):
    range: str
    count: int
    percentage: float


class CategoryBreakdownItem(BaseModel):
    name: str
    value: int
    percentage: float


class AnalyticsTrendsResponse(BaseModel):
    """Historical and distributional trend metrics for charts."""
    disputes_over_time: List[TimeSeriesTrendItem]
    risk_distribution: List[DistributionBucket]
    evidence_completeness_distribution: List[DistributionBucket]
    ai_recommendations: List[CategoryBreakdownItem]
    review_outcomes: List[CategoryBreakdownItem]
    dispute_reasons: List[CategoryBreakdownItem]


class ModelEvaluationMetrics(BaseModel):
    model_name: str
    model_version: str
    decision_threshold: float
    test_metrics: Dict[str, Any]
    baseline_metrics: Optional[Dict[str, Any]] = None
    confusion_matrix: Dict[str, int]
    top_global_features: List[Dict[str, Any]]
    threshold_analysis: List[Dict[str, Any]]
