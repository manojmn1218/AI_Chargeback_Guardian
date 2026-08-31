"""
AI Chargeback Guardian — Analytics API Endpoints (Step 7)
Provides calculated operational metrics, distribution trends, and model performance benchmarks.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    AnalyticsTrendsResponse,
    ModelEvaluationMetrics,
)

router = APIRouter()


@router.get(
    "/overview",
    response_model=AnalyticsOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Operational Analytics Overview",
)
def get_analytics_overview(db: Session = Depends(get_db)):
    """
    Retrieve real calculated summary metrics:
    - total disputes
    - open disputes
    - pending reviews
    - approved count
    - rejected count
    - recommended contest count
    - high risk dispute count
    - average case strength score
    - average evidence completeness percentage
    - recommendation distribution breakdown
    """
    try:
        service = AnalyticsService(db)
        return service.get_overview()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate analytics overview: {str(e)}",
        )


@router.get(
    "/trends",
    response_model=AnalyticsTrendsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Distribution and Historical Trend Data",
)
def get_analytics_trends(db: Session = Depends(get_db)):
    """
    Retrieve chart-ready distribution and time-series data:
    - Disputes over time
    - Risk score distribution
    - Evidence completeness distribution
    - AI recommendations breakdown
    - Human review outcomes
    - Dispute reasons breakdown
    """
    try:
        service = AnalyticsService(db)
        return service.get_trends()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate analytics trends: {str(e)}",
        )


@router.get(
    "/model",
    response_model=ModelEvaluationMetrics,
    status_code=status.HTTP_200_OK,
    summary="Get Stored ML Performance Benchmarks",
)
def get_model_benchmarks(db: Session = Depends(get_db)):
    """
    Retrieve stored model evaluation benchmarks from held-out test data.
    Does NOT retrain models during request execution.
    """
    try:
        service = AnalyticsService(db)
        return service.get_stored_model_metrics()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve model benchmarks: {str(e)}",
        )
