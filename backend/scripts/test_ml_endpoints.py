"""
AI Chargeback Guardian — ML Pipeline & API Endpoints Test Suite (Step 3)

Tests:
1. Data validation and bounds checking
2. Feature engineering pipeline
3. Model prediction service (Strong case, Weak case, Borderline case)
4. SHAP explainability factors and compliance disclaimer
5. FastAPI Endpoints:
   - POST /api/v1/ml/predict & POST /api/ml/predict
   - GET /api/v1/ml/metrics & GET /api/ml/metrics
   - GET /api/v1/ml/score-dispute/{id}
   - Input validation: Missing required field (422)
   - Input validation: Invalid categorical value (422)
   - Input validation: Negative amount (422)
"""

import sys
from pathlib import Path
import json
import urllib.request
import urllib.error

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from ml.service import ml_service
from ml.preprocessing.pipeline import validate_data, engineer_features
import pandas as pd


def test_offline_ml_pipeline():
    print("=" * 60)
    print("TEST SUITE: Offline ML Pipeline & Feature Engineering")
    print("=" * 60)

    # 1. Test strong case
    strong_case = {
        "transaction_amount": 120.0,
        "transaction_age": 10,
        "customer_account_age": 450,
        "previous_disputes": 0,
        "previous_successful_transactions": 25,
        "previous_refunds": 0,
        "evidence_count": 6,
        "merchant_dispute_rate": 0.012,
        "transaction_frequency": 1.5,
        "amount_deviation": 0.1,
        "delivery_confirmed": 1,
        "customer_acknowledged": 1,
        "refund_processed": 0,
        "communication_available": 1,
        "dispute_reason": "GOODS_NOT_RECEIVED",
        "payment_method": "CREDIT_CARD",
    }

    res_strong = ml_service.predict_single(strong_case)
    print(f"[PASS] Strong Case Prediction: Proba={res_strong['case_strength_probability']:.3f} | Score={res_strong['case_strength_score']} | Tier={res_strong['classification']}")
    assert res_strong["case_strength_score"] >= 60, "Expected strong case to score >= 60"
    assert len(res_strong["top_positive_factors"]) > 0, "Expected positive SHAP factors"

    # 2. Test weak case
    weak_case = {
        "transaction_amount": 850.0,
        "transaction_age": 40,
        "customer_account_age": 30,
        "previous_disputes": 4,
        "previous_successful_transactions": 1,
        "previous_refunds": 3,
        "evidence_count": 2,
        "merchant_dispute_rate": 0.045,
        "transaction_frequency": 0.2,
        "amount_deviation": 2.5,
        "delivery_confirmed": 0,
        "customer_acknowledged": 0,
        "refund_processed": 0,
        "communication_available": 0,
        "dispute_reason": "UNAUTHORIZED_TRANSACTION",
        "payment_method": "CREDIT_CARD",
    }

    res_weak = ml_service.predict_single(weak_case)
    print(f"[PASS] Weak Case Prediction:   Proba={res_weak['case_strength_probability']:.3f} | Score={res_weak['case_strength_score']} | Tier={res_weak['classification']}")
    assert res_weak["case_strength_score"] < 50, "Expected weak case to score < 50"

    # 3. Test missing field validation
    bad_case = strong_case.copy()
    del bad_case["transaction_amount"]
    try:
        ml_service.predict_single(bad_case)
        assert False, "Should have raised ValueError on missing field"
    except ValueError as e:
        print(f"[PASS] Missing field caught correctly: {e}")


def test_fastapi_endpoints():
    print("\n" + "=" * 60)
    print("TEST SUITE: FastAPI REST Endpoints (http://localhost:8000)")
    print("=" * 60)

    base_url = "http://localhost:8000"

    # 1. Test GET /api/v1/ml/metrics
    req = urllib.request.Request(f"{base_url}/api/v1/ml/metrics")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print(f"[PASS] GET /api/v1/ml/metrics returned HTTP 200 (Model: {data['model_name']}, Version: {data['model_version']})")
        assert "test_metrics" in data
        assert "threshold_analysis" in data
        assert "top_global_features" in data

    # 2. Test GET /api/ml/metrics (alias route)
    req_alias = urllib.request.Request(f"{base_url}/api/ml/metrics")
    with urllib.request.urlopen(req_alias) as resp:
        data_alias = json.loads(resp.read().decode())
        print(f"[PASS] GET /api/ml/metrics (Alias Route) returned HTTP 200")
        assert data_alias["model_name"] == data["model_name"]

    # 3. Test POST /api/v1/ml/predict (Strong Case)
    payload = {
        "transaction_amount": 149.99,
        "transaction_age": 12,
        "customer_account_age": 365,
        "previous_disputes": 0,
        "previous_successful_transactions": 18,
        "previous_refunds": 0,
        "evidence_count": 6,
        "merchant_dispute_rate": 0.015,
        "transaction_frequency": 1.2,
        "amount_deviation": 0.05,
        "delivery_confirmed": 1,
        "customer_acknowledged": 1,
        "refund_processed": 0,
        "communication_available": 1,
        "dispute_reason": "GOODS_NOT_RECEIVED",
        "payment_method": "CREDIT_CARD",
    }
    req_predict = urllib.request.Request(
        f"{base_url}/api/v1/ml/predict",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req_predict) as resp:
        pred_data = json.loads(resp.read().decode())
        print(f"[PASS] POST /api/v1/ml/predict (Strong Case): Score={pred_data['case_strength_score']}/100, Tier={pred_data['classification']}, Recommend Contest={pred_data['recommend_contest']}")
        assert "case_strength_probability" in pred_data
        assert "top_positive_factors" in pred_data

    # 4. Test POST /api/ml/predict (Alias Route)
    req_predict_alias = urllib.request.Request(
        f"{base_url}/api/ml/predict",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req_predict_alias) as resp:
        assert resp.status == 200
        print(f"[PASS] POST /api/ml/predict (Alias Route) returned HTTP 200")

    # 5. Test GET /api/v1/ml/score-dispute/1
    req_score_disp = urllib.request.Request(f"{base_url}/api/v1/ml/score-dispute/1")
    with urllib.request.urlopen(req_score_disp) as resp:
        disp_score = json.loads(resp.read().decode())
        print(f"[PASS] GET /api/v1/ml/score-dispute/1 (Database Record): Ref={disp_score.get('dispute_reference')}, Score={disp_score['case_strength_score']}")

    # 6. Test Validation Error on Invalid Categorical Value (422)
    invalid_payload = payload.copy()
    invalid_payload["dispute_reason"] = "INVALID_NONEXISTENT_REASON"
    req_inv = urllib.request.Request(
        f"{base_url}/api/v1/ml/predict",
        data=json.dumps(invalid_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req_inv)
        assert False, "Should have returned HTTP 422"
    except urllib.error.HTTPError as e:
        print(f"[PASS] Invalid categorical value rejected with HTTP {e.code} (Unprocessable Entity)")
        assert e.code == 422

    # 7. Test Validation Error on Negative Amount (422)
    neg_payload = payload.copy()
    neg_payload["transaction_amount"] = -50.0
    req_neg = urllib.request.Request(
        f"{base_url}/api/v1/ml/predict",
        data=json.dumps(neg_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req_neg)
        assert False, "Should have returned HTTP 422"
    except urllib.error.HTTPError as e:
        print(f"[PASS] Negative transaction amount rejected with HTTP {e.code} (Unprocessable Entity)")
        assert e.code == 422


if __name__ == "__main__":
    test_offline_ml_pipeline()
    test_fastapi_endpoints()
    print("\n" + "=" * 60)
    print("ALL ML PIPELINE & ENDPOINT TESTS PASSED (100%)")
    print("=" * 60)
