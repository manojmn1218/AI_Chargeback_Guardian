# AI Chargeback Guardian — System Limitations & Boundary Conditions

**Document Purpose:** Transparent disclosure of prototype boundaries, technical constraints, assumptions, and responsible AI guardrails.

---

## 1. Data Constraints & Synthetic Dataset Boundaries

1. **Synthetic Nature of Records:** All customers, merchants, transactions, orders, deliveries, communications, and disputes are programmatically generated synthetic records. While modeled with realistic statistical distributions and relational constraints, they do not reflect actual live bank clearing data.
2. **Simplified Network Reason Codes:** The prototype models 5 major dispute reasons (`GOODS_NOT_RECEIVED`, `UNAUTHORIZED_TRANSACTION`, `DUPLICATE_TRANSACTION`, `REFUND_NOT_RECEIVED`, `GOODS_NOT_AS_DESCRIBED`). In production, Visa and Mastercard have hundreds of granular sub-reason codes (e.g. Visa 10.4, 13.1, Mastercard 4837, 4853).
3. **Absence of Real Cardholder Identifiers:** To maintain strict data privacy compliance, no real cardholder primary account numbers (PAN), CVV codes, social security numbers, or real email addresses exist in the codebase or database.

---

## 2. Machine Learning Model Boundaries

1. **Static Model Artifacts:** The current XGBoost model ($v1.0$) was trained on 850 synthetic training records and evaluated on 150 held-out test records. It does not perform online continuous retraining upon every human reviewer decision.
2. **Tabular Feature Dependency:** The ML engine evaluates 29 structured tabular features. It does not natively ingest unformatted unstructured PDF attachments or perform computer vision OCR on scanned physical courier waybills in this prototype version.
3. **Correlation vs. Causality:** Local TreeSHAP attributions indicate mathematical model feature importance within the decision trees, not definitive causal proof of arbitration outcome. All explanation panels display the required compliance notice.

---

## 3. Generative AI & LLM Boundaries

1. **Dual Provider Architecture:** When external LLM API credentials (`LLM_API_KEY`) are not configured, the system seamlessly operates in **Deterministic Demo Mode (`DemoLLMProvider`)**. While this guarantees 100% uptime and zero cost during local demonstrations, it produces structured template rebuttals rather than emergent natural language.
2. **Context Window & Prompt Constraints:** Prompts are capped to verified facts and relevant merchant policies to prevent context degradation and maintain sub-second response latency.

---

## 4. Legal & Regulatory Compliance Disclaimers

1. **Decision Support Only:** AI Chargeback Guardian is strictly an automated decision-support tool. It does not constitute legal representation or binding arbitration advice.
2. **Mandatory Human Authorization:** In compliance with financial risk governance standards, the system prohibits autonomous chargeback submission. A human operator must review and authorize every formal dispute rebuttal.
