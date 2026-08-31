"""
AI Chargeback Guardian — API v1 Router Aggregator
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health, disputes, customers, merchants, transactions, ml, analytics, export, webhooks

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(merchants.router, prefix="/merchants", tags=["Merchants"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(disputes.router, prefix="/disputes", tags=["Disputes"])
api_router.include_router(ml.router, prefix="/ml", tags=["Machine Learning"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(export.router, prefix="/export", tags=["Export & Documents"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Gateway Webhooks"])

router = api_router


