# AI Chargeback Guardian — REST API Reference

**Base URL:** `http://localhost:8000/api/v1` (with convenience aliases at `/api/*`)  
**Specification:** OpenAPI 3.0 (Interactive Swagger available at `http://localhost:8000/docs`)

---

## 1. System Health

### `GET /health` / `GET /api/v1/health`
Checks application health and database connection.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "app_name": "AI Chargeback Guardian",
  "version": "0.1.0"
}
```

---

## 2. Disputes & Relational Entities

### `GET /api/v1/disputes`
List disputes with pagination and filtering.

**Query Parameters:**
- `page` (int, default: 1): Page number.
- `page_size` (int, default: 20): Items per page.
- `status` (string, optional): Filter by `OPEN`, `UNDER_REVIEW`, `RESOLVED`, `CLOSED`.
- `reason` (string, optional): Filter by dispute reason code.

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "dispute_reference": "DISP-000001",
      "transaction_id": 5068,
      "customer_id": 482,
      "merchant_id": 29,
      "dispute_reason": "GOODS_NOT_RECEIVED",
      "dispute_amount": 168.25,
      "dispute_status": "RESOLVED",
      "dispute_timestamp": "2026-06-11T07:00:00"
    }
  ],
  "total": 1000,
  "page": 1,
  "page_size": 20
}
```

### `GET /api/v1/disputes/{id}`
Retrieve full dispute detail including linked Customer, Merchant, Transaction, and Evidence items.

---

## 3. Evidence Intelligence Engine

### `GET /api/v1/disputes/{id}/investigation`
Retrieves comprehensive evidence dossier including 7-category completeness, quality score, chronological timeline, and consistency warnings.

**Response (200 OK):**
```json
{
  "dispute": { ... },
  "evidence_analysis": {
    "total_expected": 7,
    "available": 6,
    "verified": 6,
    "missing": 1,
    "availability_percentage": 85.7,
    "verification_percentage": 85.7,
    "quality_score": 90.0,
    "evidence_checklist": [
      {
        "evidence_type": "PAYMENT",
        "category_display_name": "Payment Authorization & 3DS Log",
        "description": "3DS Verified authorization log",
        "source_reference": "GATEWAY_3DS_AUTH",
        "available": true,
        "verified": true,
        "status": "AVAILABLE_VERIFIED"
      }
    ],
    "strongest_evidence": [ ... ],
    "missing_evidence": [ ... ]
  },
  "ml_analysis": {
    "probability": 0.85,
    "score": 85,
    "classification": "STRONG",
    "recommend_contest": true
  },
  "timeline": [ ... ],
  "warnings": [ ... ]
}
```

### `GET /api/v1/disputes/{id}/timeline`
Returns chronological milestones (Transaction, Order, Shipment, Delivery, Communication, Dispute).

---

## 4. Machine Learning & TreeSHAP Explainability

### `POST /api/v1/ml/predict`
Calculates case strength and local TreeSHAP attribution for a feature payload.

**Request Body:**
```json
{
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
  "payment_method": "CREDIT_CARD"
}
```

### `GET /api/v1/disputes/{id}/explanation`
Retrieves local TreeSHAP attributions and waterfall drivers for a stored dispute.

**Response (200 OK):**
```json
{
  "dispute_id": 1,
  "dispute_reference": "DISP-000001",
  "score": 85,
  "classification": "STRONG",
  "prediction_probability": 0.85,
  "top_positive_factors": [
    {
      "feature_name": "transaction_amount",
      "display_name": "Dispute Transaction Amount",
      "feature_value": 168.25,
      "contribution": 0.469,
      "impact_pct": "+46.9%",
      "direction": "POSITIVE",
      "description": "Increases win confidence"
    }
  ],
  "top_negative_factors": [ ... ],
  "disclaimer": "Model contribution — not causal proof."
}
```

---

## 5. Grounded AI Response Engine

### `POST /api/v1/disputes/{id}/ai-response`
Generates an evidence-grounded draft rebuttal letter with strict anti-hallucination checks.

**Request Body (Optional):**
```json
{
  "force_refresh": false,
  "custom_instructions": null
}
```

**Response (200 OK):**
```json
{
  "dispute_id": 1,
  "dispute_reference": "DISP-000001",
  "case_summary": "Dispute DISP-000001 for $168.25 was reviewed...",
  "recommended_action": "CONTEST",
  "draft_response": "FORMAL CHARGEBACK REBUTTAL STATEMENT\n...",
  "evidence_references": [
    "[EVIDENCE: PAYMENT]",
    "[EVIDENCE: DELIVERY]",
    "[POLICY: SHIPPING_POLICY]"
  ],
  "grounding_status": "VERIFIED",
  "grounding_validation": {
    "is_valid": true,
    "status": "VERIFIED",
    "passed_checks": [ ... ],
    "failed_checks": [],
    "invalid_references": []
  },
  "confidence": {
    "confidence_score": 88,
    "confidence_level": "HIGH",
    "disclaimer": "Application-level heuristic confidence indicator..."
  },
  "is_fallback": true
}
```

---

## 6. Human Review & Approval

### `GET /api/v1/disputes/{id}/review`
Returns current review status, original AI draft, and authorization history.

### `POST /api/v1/disputes/{id}/review`
Submits human reviewer authorization.

**Request Body:**
```json
{
  "decision": "EDIT_AND_APPROVE",
  "reviewer_reference": "REV-00892",
  "edited_response": "CUSTOM EDITED FORMAL REBUTTAL SUBMISSION...",
  "reviewer_notes": "Verified carrier GPS logs match shipping address."
}
```

*Enforcement:* Approval is blocked with HTTP 422 if `grounding_status == "FAILED"`. Reviewer notes are required for `NEEDS_MORE_EVIDENCE`.

---

## 7. Immutable Audit Trail

### `GET /api/v1/disputes/{id}/audit`
Retrieves chronological audit events.

---

## 8. Analytics Engine

### `GET /api/v1/analytics/overview`
Calculates live portfolio summary statistics:
- `total_disputes`, `open_disputes`, `pending_reviews`, `approved`, `rejected`
- `average_case_strength`, `average_evidence_completeness`, `total_amount_at_risk`
- `recommendation_distribution`

### `GET /api/v1/analytics/trends`
Returns time-series and distribution buckets for charts.

### `GET /api/v1/analytics/model`
Returns stored held-out test evaluation benchmarks without retraining.
