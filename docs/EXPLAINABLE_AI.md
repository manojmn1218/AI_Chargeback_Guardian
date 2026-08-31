# AI Chargeback Guardian — Explainable AI & SHAP Feature Attribution (Step 6)

## Overview & Philosophy

The **Explainability Layer** translates complex ensemble tree decisions (XGBoost / Gradient Boosting) into transparent, auditable feature attributions for payment risk officers, fraud analysts, and issuing bank arbitration committees.

---

## 1. TreeSHAP Attribution Engine

The platform utilizes **TreeSHAP** (Lundberg et al.), an exact, polynomial-time algorithm for calculating Shapley values for tree-based ensemble models:

$$\phi_i = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!(|F| - |S| - 1)!}{|F|!} \left[ f_x(S \cup \{i\}) - f_x(S) \right]$$

- **Local Waterfall Attributions**: Computes the exact marginal contribution $\phi_i$ of each feature $i$ for an individual dispute.
- **Base Value ($E[f(x)]$ )**: The expected win probability across the synthetic training population (e.g. 50%).
- **Score Formulation**: Sum of base value and all individual feature attributions maps directly to model win probability:
  $$\hat{p} = \text{logit}^{-1}\left( \phi_0 + \sum_{i=1}^M \phi_i \right)$$

---

## 2. Distinction: Statistical Contribution vs. Legal Causation

### Mandatory Regulatory & Compliance Notice:
> **Model explanations represent mathematical contributing factors within the ML decision surface and do NOT constitute guaranteed legal causation under card network arbitration rules.**

- **Accepted Terminology**: *"Contributing factor"*, *"Win probability driver"*, *"Evidentiary weight"*.
- **Prohibited Terminology**: *"This caused the dispute"*, *"This legally guarantees an arbitration victory"*.

---

## 3. Positive vs. Negative Feature Drivers

| Direction | Impact on Win Probability | Example Features | Operational Meaning |
| :--- | :--- | :--- | :--- |
| **Positive (+)** | Increases merchant win likelihood | `delivery_confirmed`, `customer_acknowledged`, `evidence_count >= 6` | Solid courier proof and verified customer delivery acknowledgement strengthen merchant contest posture. |
| **Negative (-)** | Decreases merchant win likelihood / elevates risk | `dispute_reason_UNAUTHORIZED`, `amount_deviation > 2.5`, `refund_processed = 0` | Unusual transaction spike or card-not-present fraud claim without 3DS authentication elevates merchant vulnerability. |

---

## 4. Graceful Fallback Strategy

In environments where C-extensions or the `shap` library cannot be initialized:
1. The service automatically switches to `MODEL_FEATURE_IMPORTANCE_FALLBACK`.
2. Clearly sets `"method": "MODEL_FEATURE_IMPORTANCE_FALLBACK"` in the API response.
3. Computes heuristic directional weights from preprocessed feature matrices without crashing inference or blocking dispute investigations.

---

## 5. API Data Contract (`GET /api/v1/disputes/{id}/explanation`)

```json
{
  "dispute_id": "1",
  "dispute_reference": "DISP-000001",
  "model_version": "v1.0",
  "model_name": "xgboost",
  "score": 85,
  "classification": "STRONG",
  "prediction_probability": 0.8502,
  "base_value": -0.1272,
  "top_positive_factors": [
    {
      "feature": "num__transaction_amount",
      "display_name": "Dispute Transaction Amount",
      "contribution": 0.4688,
      "direction": "positive",
      "impact_pct": "+46.9%"
    },
    {
      "feature": "bin__customer_acknowledged",
      "display_name": "Customer Acknowledged Receipt",
      "contribution": 0.3114,
      "direction": "positive",
      "impact_pct": "+31.1%"
    }
  ],
  "top_negative_factors": [
    {
      "feature": "num__merchant_dispute_rate",
      "display_name": "Merchant Historical Dispute Rate",
      "contribution": -0.1587,
      "direction": "negative",
      "impact_pct": "-15.9%"
    }
  ],
  "method": "SHAP",
  "disclaimer": "Model explanations represent mathematical contributing factors within the predictive model and do NOT constitute guaranteed legal causation under card network arbitration rules."
}
```
