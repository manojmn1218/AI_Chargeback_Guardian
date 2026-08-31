# AI Chargeback Guardian

> **Enterprise-grade Chargeback Defense Platform:** Autonomous Risk Assessment, Deterministic Evidence Intelligence, Grounded AI Rebuttal Generation, TreeSHAP Explainability, and Human-in-the-Loop Governance.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19.0-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF.svg)](https://vitejs.dev/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0+-FF6600.svg)](https://xgboost.readthedocs.io/)
[![SHAP](https://img.shields.io/badge/SHAP-0.45+-brightgreen.svg)](https://shap.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 1. Overview & Problem Statement

E-commerce merchants lose over **$100 billion annually** to friendly fraud, chargeback abuse, and operational inefficiencies. When a customer files a dispute, merchants have a strict window to submit a formal rebuttal letter backed by conclusive evidence (e.g. 3DS authentication logs, carrier proof of delivery, signed terms of service).

### Why Traditional Chargeback Workflows Fail:
1. **Evidence Fragmentation:** Relevant records are scattered across gateway logs, warehouse ERPs, courier portals, customer support chats, and terms of service.
2. **High Investigation Cost:** A human fraud specialist spends 30 to 45 minutes manually collating evidence for a single dispute.
3. **The LLM Hallucination Hazard:** Generic LLMs frequently fabricate non-existent delivery confirmations or incorrect tracking numbers, resulting in severe card network arbitration penalties and merchant account termination.

### The AI Chargeback Guardian Solution:
**AI Chargeback Guardian** combines **supervised machine learning (XGBoost)**, **local feature attribution (TreeSHAP)**, a **7-category relational evidence intelligence matrix**, **deterministic anti-hallucination guardrails**, and **human-in-the-loop review** into an auditable, enterprise-ready decision platform.

---

## 2. System Architecture

```
+-----------------------------------------------------------------------------------+
|                                 FRONTEND (React 19 + Vite 6)                      |
|  - Real-time Command Deck (6 KPI Cards, Recharts Volume Trends & Recommendation)  |
|  - Investigation Dossier (7-Category Evidence Matrix, Carrier Tracking, Timelines)|
|  - TreeSHAP Local Explainability Waterfall (Compliant Driver Attributions)        |
|  - Grounded AI Rebuttal Editor & Grounding Status Indicator                       |
|  - Human Review Gate (Approve, Edit & Approve, Reject, Needs Evidence)           |
|  - Operational & Model Analytics (Held-Out Evaluation Benchmarks & Cost Curves)   |
+------------------------------------------+----------------------------------------+
                                           | REST APIs (/api/v1/*)
                                           v
+-----------------------------------------------------------------------------------+
|                                 BACKEND (FastAPI + SQLAlchemy 2.0)                |
|  +------------------+  +----------------------+  +-----------------------------+  |
|  | Relational ORM   |  | Evidence Intelligence|  | ML Risk & TreeSHAP          |  |
|  | - 12 DB Tables   |  | - 7 Categories       |  | - XGBoost Classifier        |  |
|  | - Foreign Keys   |  | - Quality Score      |  | - Optimal Tau = 0.60 Gate   |  |
|  | - 1,000 Disputes |  | - Consistency Checks |  | - Local Attribution Driver  |  |
|  +------------------+  +----------------------+  +-----------------------------+  |
|           |                       |                            |                  |
|           +-----------------------+----------------------------+                  |
|                                   |                                               |
|                                   v                                               |
|  +-----------------------------------------------------------------------------+  |
|  | Grounded AI / RAG Response Engine & Anti-Hallucination Guardrail            |  |
|  | - Strict Fact Dossier Compilation (Excludes Missing/Unverified Records)    |  |
|  | - Deterministic Grounding Validator (Blocks Fake Delivery / Refund Claims)  |  |
|  | - Application Confidence Heuristic (0 to 100)                              |  |
|  | - Offline Deterministic Fallback Demo Provider (Zero API Key Dependency)    |  |
|  +-----------------------------------------------------------------------------+  |
|                                   |                                               |
|                                   v                                               |
|  +-----------------------------------------------------------------------------+  |
|  | Human-in-the-Loop Review State Machine & Immutable Audit Trail Log         |  |
|  | - Review Decisions: APPROVE, EDIT_AND_APPROVE, REJECT, NEEDS_MORE_EVIDENCE   |  |
|  | - Approval Blocked if Grounding Status == FAILED                           |  |
|  | - Immutable Audit Events Tracked (SYSTEM, AI, HUMAN Actors)                |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 3. Empirical Machine Learning Benchmarks

The ML Risk Engine uses an **XGBoost Classifier** evaluated on a strictly partitioned **15% held-out test split ($N=150$)** with zero data leakage:

| Evaluation Metric | XGBoost (Champion) | Logistic Regression (Baseline) | Operational Interpretation |
| :--- | :--- | :--- | :--- |
| **Optimal Threshold ($\tau$)** | **0.60** | **0.50** | Calibrated on asymmetric financial risk |
| **Precision** | **83.75% (0.8375)** | 85.39% (0.8539) | High accuracy on recommended contests |
| **Recall (Sensitivity)** | **63.81% (0.6381)** | 72.38% (0.7238) | Recovers nearly two-thirds of winnable disputes |
| **F1 Score** | **0.7243** | 0.7835 | Harmonic balance of precision and recall |
| **PR-AUC** | **0.8716** | 0.8687 | Strong discrimination across positive cases |
| **ROC-AUC** | **0.7532** | 0.7805 | Overall ranking capability |
| **False Positive Rate (FPR)** | **28.89% (0.2889)** | 28.89% (0.2889) | Minimizes futile arbitration fees |
| **False Negative Rate (FNR)** | **36.19% (0.3619)** | 27.62% (0.2762) | Conservative win probability gate |

### Asymmetric Risk Model & Threshold Calibration
In payment arbitration, losing an ungrounded dispute costs a **$\$15$ filing fee**, while forfeiting a winnable dispute loses the full transaction amount (average **$\$489$**). Sweeping $\tau \in [0.10, 0.90]$ demonstrates that **$\tau = 0.60$** provides optimal operational balance.

---

## 4. Key Platform Features

### 1. 7-Category Evidence Intelligence Engine
Standardizes evidence into 7 structured categories:
1. **Payment Authorization:** Gateway 3DS verification and CVV match logs.
2. **Billing Invoice:** Transaction invoice and line items.
3. **Order Cart:** Itemized order records and digital cart logs.
4. **Fulfillment & Delivery:** Courier GPS tracking and customer signature confirmation.
5. **Refund / Credit:** Proof of prior refund or credit attempts.
6. **Customer Communications:** Support tickets, emails, and delivery acknowledgements.
7. **Merchant Policy:** Active terms of service, shipping policy, and cancellation policy.

Calculates exact mathematical **Availability %**, **Verification %**, a weighted **Quality Score (0 to 100)**, and flags **Consistency Warnings** (e.g. amount discrepancies, impossible timestamps).

### 2. Zero-Hallucination Grounded AI Rebuttal Engine
- Strictly compiles verified facts from SQLite records into prompt context.
- Generates structured JSON rebuttal letters with traceable citations (`[EVIDENCE: PAYMENT]`, `[POLICY: SHIPPING_POLICY]`).
- The **Grounding Validator** algorithmically verifies citations and blocks drafts claiming unconfirmed deliveries or absent refunds.

### 3. Local TreeSHAP Explainability
- Evaluates exact TreeSHAP waterfall feature contributions for every dispute.
- Surfaces top positive and negative drivers with the mandatory compliance disclaimer: *"Model contribution — not causal proof."*

### 4. Human-in-the-Loop Review & Governance Gate
- Prohibits autonomous submissions to financial institutions.
- Specialists can **Approve**, **Edit & Approve**, **Reject**, or request **More Evidence**.
- Approval is programmatically disabled if grounding validation fails.

### 5. Immutable Audit Trail
- Every dispute lifecycle milestone is permanently recorded in `audit_logs` with timestamps, actor IDs, and structured JSON metadata.

---

## 5. Quickstart & Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 1. Clone & Environment Setup
```bash
git clone https://github.com/manojmn1218/AI_Chargeback_Guardian.git
cd AI_Chargeback_Guardian

# Copy environment template
cp .env.example .env
```


### 2. Backend Setup & Seeding
```bash
# Create and activate Python virtual environment
python -m venv backend/venv
source backend/venv/bin/activate  # On Linux/macOS
backend\venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Seed 1,000 synthetic disputes and demo scenarios
python scripts/seed_demo.py

# Start FastAPI backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Backend API Documentation is available at: `http://localhost:8000/docs`*

### 3. Frontend Setup
```bash
# In a new terminal window:
cd frontend
npm install
npm run dev
```
*Frontend Application is available at: `http://localhost:5173`*

---

## 6. Running Tests & Quality Verification

Run the master test suite to verify all 7 layers of the system:
```bash
python scripts/run_all_tests.py
```
**Expected Result:** `>>> ALL 18/18 REGRESSION & SYSTEM INTEGRATION TESTS PASSED (100%) <<<`

### Individual Component Test Suites:
```bash
python backend/scripts/test_evidence_engine.py  # Evidence & Quality Scoring
python backend/scripts/test_ai_response.py      # Grounding & Anti-Hallucination
python backend/scripts/test_step6.py            # SHAP, Human Review & Audit Trail
```

### Production Build Verification:
```bash
cd frontend
npm run build
```

---

## 7. Demonstration Showcase Scenarios

| Reference | Scenario Description | Reason Code | Case Amount | Defensive Tier |
| :--- | :--- | :--- | :--- | :--- |
| **`DISP-000001`** | Strong Evidence Rebuttal (High Win Prob) | `GOODS_NOT_RECEIVED` | $168.25 | **STRONG (CONTEST)** |
| **`DISP-000002`** | Weak Evidence / High Risk Defense | `UNAUTHORIZED_TRANSACTION` | $101.74 | **WEAK (REVIEW/ACCEPT)** |
| **`DISP-000003`** | Missing Evidence / Grounding Guardrail | `UNAUTHORIZED_TRANSACTION` | $16.16 | **WEAK (NEEDS EVIDENCE)** |
| **`DISP-000004`** | Conflicting Evidence Warning Test | `DUPLICATE_TRANSACTION` | $24.99 | **WARNING CHECK** |
| **`DISP-000005`** | Medium-Risk / Human Discretion Case | `DUPLICATE_TRANSACTION` | $103.50 | **STRONG (CONTEST)** |

---

## 8. Documentation Suite Index

Detailed architectural, mathematical, and operational documentation is located in the [`docs/`](./docs/) directory:

- [`docs/FINAL_ARCHITECTURE_AUDIT.md`](./docs/FINAL_ARCHITECTURE_AUDIT.md) — Complete architecture audit and remediation report.
- [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) — System architecture, data flow, and technology stack.
- [`docs/ML_METHODOLOGY.md`](./docs/ML_METHODOLOGY.md) — Empirical ML training, evaluation metrics, and cost curve analysis.
- [`docs/EVIDENCE_ENGINE.md`](./docs/EVIDENCE_ENGINE.md) — 7-category evidence matrix and quality scoring formulas.
- [`docs/AI_RESPONSE_ENGINE.md`](./docs/AI_RESPONSE_ENGINE.md) — Grounded AI prompt construction and anti-hallucination validation.
- [`docs/HUMAN_REVIEW.md`](./docs/HUMAN_REVIEW.md) — Review state machine and approval safeguard rules.
- [`docs/EXPLAINABLE_AI.md`](./docs/EXPLAINABLE_AI.md) — TreeSHAP attributions and compliance disclaimers.
- [`docs/API_REFERENCE.md`](./docs/API_REFERENCE.md) — Comprehensive OpenAPI/REST API documentation.
- [`docs/DEMO_GUIDE.md`](./docs/DEMO_GUIDE.md) — 5-minute timed live walkthrough guide.
- [`docs/PITCH_SCRIPT.md`](./docs/PITCH_SCRIPT.md) — Concise executive pitch script.
- [`docs/LIMITATIONS.md`](./docs/LIMITATIONS.md) — System boundaries and responsible AI disclaimers.
- [`docs/DEPLOYMENT.md`](./docs/DEPLOYMENT.md) — Local and production deployment procedures.
- [`docs/SUBMISSION_CHECKLIST.md`](./docs/SUBMISSION_CHECKLIST.md) — Final verified submission checklist.
- [`docs/FINAL_VALIDATION_REPORT.md`](./docs/FINAL_VALIDATION_REPORT.md) — Full validation report.

---

## 9. Security & Responsible AI Disclaimers

- **Synthetic Data Notice:** All records in this project are 100% synthetically generated. No real cardholder PANs, CVVs, credentials, or personal information exist in this codebase.
- **Decision-Support Only:** AI Chargeback Guardian provides decision support and does not constitute legal or financial arbitration advice.
- **Mandatory Human Oversight:** Automated chargeback submission is prohibited; all formal contest filings require human reviewer authorization.

---

## 10. License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
