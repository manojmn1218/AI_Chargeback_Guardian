# AI Chargeback Guardian — System Architecture Documentation

**System Version:** 0.1.0  
**Status:** Integrated & Verified  
**Dataset:** 100% Synthetic Relational Records (No real PII / Financial Credentials)

---

## 1. System Overview

**AI Chargeback Guardian** is an enterprise-grade prototype designed to assist merchant fraud risk and payment operations teams in investigating, predicting, and contesting payment chargebacks. 

Rather than relying on generic LLM wrappers that fabricate facts, AI Chargeback Guardian combines **relational evidence retrieval**, **supervised machine learning (XGBoost)**, **local feature attribution (TreeSHAP)**, **deterministic anti-hallucination guardrails**, and **human-in-the-loop review** into an auditable, end-to-end decision workflow.

```
+-----------------------------------------------------------------------------------+
|                                FRONTEND LAYER                                     |
|  React 19 + Vite 6 + TailwindCSS v4 + Recharts + Lucide Icons + Cyberpunk Audio FX |
|                                                                                   |
|   [Command Deck]     [Investigation Dossier]    [Benchmark Analytics]             |
|   - 6 KPI Cards      - 7-Category Checklist     - Held-Out Model Benchmarks       |
|   - Recharts Trends  - TreeSHAP Waterfall       - Asymmetric Risk Cost Curve      |
|   - Paginated Table  - Human Review Gate        - Confusion Matrix Breakdown      |
+------------------------------------------+----------------------------------------+
                                           | REST APIs (/api/v1/* & /api/*)
                                           v
+-----------------------------------------------------------------------------------+
|                                 BACKEND LAYER                                     |
|                       FastAPI + Pydantic v2 + SQLAlchemy 2.0                      |
|                                                                                   |
|  +------------------+  +----------------------+  +-----------------------------+  |
|  | Dispute & Entity |  | Evidence Engine      |  | ML Risk & TreeSHAP          |  |
|  | Service          |  | - Availability %     |  | - XGBoost Champion Model    |  |
|  | - 12 Tables      |  | - Quality Score      |  | - Tau=0.60 Decision Gate    |  |
|  | - Foreign Keys   |  | - Consistency Checks |  | - Local Attribution Driver  |  |
|  +------------------+  +----------------------+  +-----------------------------+  |
|           |                       |                            |                  |
|           +-----------------------+----------------------------+                  |
|                                   |                                               |
|                                   v                                               |
|  +-----------------------------------------------------------------------------+  |
|  | Grounded AI / RAG Response Engine & Human-in-the-Loop Gateway               |  |
|  | - Strict Anti-Hallucination Guardrail (Blocks unverified/missing claims)    |  |
|  | - Traceable Evidence Citations ([EVIDENCE: PAYMENT], [POLICY: SHIPPING])   |  |
|  | - Transparent Confidence Scoring (Heuristic 0-100 indicator)                |  |
|  | - Human Review State Machine (APPROVE, EDIT_AND_APPROVE, REJECT, NEEDS_EV) |  |
|  | - Immutable Audit Logger (SYSTEM, AI, HUMAN actor events)                   |  |
|  +-----------------------------------------------------------------------------+  |
|                                   |                                               |
|                                   v                                               |
|  +-----------------------------------------------------------------------------+  |
|  | Analytics Aggregator Engine                                                 |  |
|  | - Live Overview Summary (Disputes, Pending, Approved, Risk, Completeness)  |  |
|  | - Time-Series & Distribution Trends for Recharts UI                         |  |
|  | - Zero Retraining during runtime analytics requests                        |  |
|  +-----------------------------------------------------------------------------+  |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                                DATA & MODEL ARTIFACTS                             |
|  SQLite Database (`chargeback_guardian.db`) | XGBoost Model Artifacts (.joblib)   |
|  1,000 Disputes | 7,000 Evidence Items | 6,000 Transactions | 750 Customers       |
+-----------------------------------------------------------------------------------+
```

---

## 2. Core Architectural Pillars

### Pillar 1: Deterministic Relational Grounding
All dispute metadata, payment logs, orders, courier tracking, customer communications, refund logs, and merchant policies are modeled in an ACID-compliant relational SQLite database with strict foreign key integrity. The AI engine NEVER generates claims from unstructured memory; it is strictly constrained to verified database records.

### Pillar 2: Empirical Supervised ML Risk Prediction
The system runs a trained **XGBoost Classifier** ($N=1,000$, held-out test $N=150$) that outputs a continuous win probability ($0.0$ to $1.0$), a normalized case strength score ($0$ to $100$), and an operational classification (`STRONG`, `NEEDS_REVIEW`, `WEAK`).

### Pillar 3: TreeSHAP Feature Attribution & Local Explainability
For every prediction, the system computes exact TreeSHAP feature contributions, displaying the top positive and negative drivers of the win probability with an explicit compliance disclaimer (*"Model contribution — not causal proof."*).

### Pillar 4: Anti-Hallucination Validation & Citation Checking
Before presenting any AI rebuttal to the human reviewer, the **Grounding Validator** inspects the draft text:
- Verifies that all cited references exist in the dispute's evidence records.
- Flags and fails drafts claiming delivery when `delivery_confirmed=False`.
- Flags and fails drafts claiming refunds when `refund_status != 'PROCESSED'`.
- Blocks human approval if grounding validation status is `FAILED`.

### Pillar 5: Human-in-the-Loop Decision Layer
AI drafts are never sent automatically to issuing banks. A human specialist must review the dossier, inspect the TreeSHAP explanation, and choose:
1. `APPROVE` — Authorize original AI draft.
2. `EDIT_AND_APPROVE` — Customize draft and authorize.
3. `REJECT` — Accept chargeback loss without contest.
4. `NEEDS_MORE_EVIDENCE` — Request additional courier/customer proof (requires mandatory notes).

### Pillar 6: Immutable Audit Trail
Every lifecycle event (dispute ingestion, evidence retrieval, ML inference, AI draft generation, grounding check, human review, and edits) is stored in the `audit_logs` table with timestamps, actor types (`SYSTEM`, `AI`, `HUMAN`), and structured metadata.

---

## 3. Technology Stack

- **Backend:** Python 3.11+, FastAPI 0.115, Pydantic v2, SQLAlchemy 2.0, Uvicorn, Pandas, NumPy, Scikit-Learn 1.4+, XGBoost 2.0+, SHAP 0.45+.
- **Frontend:** React 19, Vite 6, TailwindCSS v4, Recharts 2.15, Lucide React icons, Web Audio API synth sounds.
- **Database:** SQLite 3 with concurrency pragmas (`PRAGMA journal_mode=MEMORY`, `PRAGMA synchronous=OFF`).
- **Packaging & Testing:** Pytest, Starlette TestClient, Axios interceptors.
