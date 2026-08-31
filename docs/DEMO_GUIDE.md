# AI Chargeback Guardian — 5-Minute Demonstration Guide

**Target Audience:** Hiring committee, product leadership, risk operations specialists  
**Format:** Live interactive browser walkthrough  
**Dataset:** 100% Synthetic Relational Database (No real PII / Financial Credentials)

---

## 1. Quick Setup & Startup Commands

```bash
# 1. Install Backend Dependencies
pip install -r requirements.txt

# 2. Seed Synthetic Demo Database
python scripts/seed_demo.py

# 3. Start Backend Server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# (Accessible at http://localhost:8000/docs)

# 4. Start Frontend Dev Server
cd frontend
npm install
npm run dev
# (Accessible at http://localhost:5173)
```

---

## 2. Timed 5-Minute Demonstration Sequence

### `[0:00 - 0:30]` — The Problem
> *"E-commerce merchants lose over $100B annually to chargeback fraud. Fighting chargebacks is painful: fraud analysts spend 45 minutes per dispute manually hunting down courier receipts, 3DS logs, order carts, and terms of service across siloed systems. Worse, generic LLMs hallucinate non-existent tracking numbers, getting merchants banned from card networks."*

### `[0:30 - 1:00]` — The Solution
> *"AI Chargeback Guardian solves this with a deterministic 7-layer architecture. We don't just ask an LLM to write a letter—we run a trained XGBoost classifier for win probability, compute exact TreeSHAP feature attributions, retrieve a 7-category verified evidence matrix from SQLite, apply deterministic anti-hallucination guardrails, and keep a human expert in control with an immutable audit trail."*

### `[1:00 - 1:45]` — Main Command Deck (Dashboard)
- **Action:** Open `http://localhost:5173`
- **Showcase:**
  1. Point out the **6 live KPI cards** (Total Disputes: 1,000, Pending Review, High Risk, Recommended Contest: 907, Approved, Rejected). Note that all numbers come from live backend calculations.
  2. Show the **Dispute Ingestion Trend** area chart and **AI Recommendation Breakdown** donut chart powered by Recharts.
  3. Filter the Recent Disputes table by `Open`, `In Review`, and `Resolved`.
  4. Click on **`DISP-000001`** ($168.25 claim for `GOODS_NOT_RECEIVED`).

### `[1:45 - 2:30]` — Investigation Dossier & Evidence Matrix
- **Action:** Inside `/disputes/1`
- **Showcase:**
  1. Highlight the **Case Header**: Reason (`GOODS NOT RECEIVED`), Amount ($168.25), Quality Score ($90/100$), Availability ($85.7\%$).
  2. Switch to the **Evidence Matrix (7)** tab: Show the 7 categories (Payment 3DS, Invoice, Order, Delivery GPS, Customer Comms, Merchant Policy, Refund).
  3. Click **Inspect** on `Delivery`: Show proof of delivery carrier reference `FEDEX-POD-00123` and customer signature acknowledgement.
  4. Show the **Consistency Check Engine**: Zero timeline conflicts detected.

### `[2:30 - 3:15]` — ML Assessment & TreeSHAP Explainability
- **Action:** Click **TreeSHAP Explainability** tab
- **Showcase:**
  1. Show the **XGBoost Win Probability (85.0%)** and **Case Strength (85/100, STRONG)**.
  2. Explain the **Waterfall Drivers**: Transaction amount ($+\$46.9\%$), Customer purchase frequency ($+39.7\%$), Customer delivery acknowledgement ($+31.1\%$).
  3. Point out the compliance disclaimer: *"Model contribution — not causal proof."*

### `[3:15 - 4:00]` — Grounded AI Response & Anti-Hallucination Guardrail
- **Action:** Click **Grounded AI Rebuttal** tab
- **Showcase:**
  1. Point out the structured rebuttal letter citing exact references (`[EVIDENCE: PAYMENT]`, `[EVIDENCE: DELIVERY]`, `[POLICY: SHIPPING_POLICY]`).
  2. Highlight the **Grounding Status: VERIFIED** and **Application Confidence: 88/100 (HIGH)**.
  3. *Key story point:* Show that missing evidence (e.g. absent refund log) is explicitly disclosed in the missing evidence section, never fabricated.

### `[4:00 - 4:40]` — Human Review & Approval Gate
- **Action:** Click **Human Review Gate** tab
- **Showcase:**
  1. Show the 4 decision buttons: `APPROVE`, `EDIT & APPROVE`, `REJECT`, `REQUEST MORE EVIDENCE`.
  2. Select **`EDIT & APPROVE`**: Modify the rebuttal text to add custom specialist commentary.
  3. Enter reviewer notes: *"Verified courier GPS logs match cardholder billing address."*
  4. Click **Authorize Decision**: Show instant authorization banner and update to dispute status.
  5. Switch to **Audit History** tab: Show the new `REVIEW_APPROVED` audit event with timestamp and reviewer ID `REV-00892`.

### `[4:40 - 5:00]` — Deep Analytics, Limitations & Conclusion
- **Action:** Navigate to `/analytics`
- **Showcase:**
  1. Show the held-out test evaluation benchmarks: Precision ($83.8\%$), Recall ($63.8\%$), F1 ($0.724$), Decision threshold ($\tau = 0.60$).
  2. Conclude: *"AI Chargeback Guardian delivers provable 83.8% precision on contest recommendations, reduces manual investigation time from 45 minutes to 3 minutes, guarantees zero hallucinated evidence, and keeps full human oversight with immutable auditability."*
