# AI Chargeback Guardian — Executive Pitch & Presentation Script

**Project Title:** AI Chargeback Guardian  
**Tagline:** Autonomous Risk Assessment, Deterministic Evidence Intelligence & Human-in-the-Loop Chargeback Defense  

---

## 1. The Problem: The $100B Chargeback Tax
When a consumer disputes a charge with their issuing bank, the merchant is immediately penalized with a chargeback fee and forfeited revenue. In friendly fraud and chargeback abuse cases, merchants have the legal right to submit a formal rebuttal containing evidence.

However, modern chargeback operations suffer from three critical bottlenecks:
1. **Evidence Fragmentation:** Proof of delivery, 3DS authentication logs, order carts, and customer support chats live in isolated, incompatible silos.
2. **Operational Latency:** A human fraud analyst spends 30 to 45 minutes manually assembling documentation for a single $150 dispute.
3. **The Generative AI Hallucination Trap:** Applying generic LLM prompt wrappers directly to financial arbitration is dangerous. Unconstrained LLMs hallucinate non-existent delivery confirmations, invalid timestamps, or fake tracking numbers, exposing merchants to severe card network compliance fines and arbitration bans.

---

## 2. Our Solution: Deterministic Evidence Intelligence + Grounded AI
**AI Chargeback Guardian** is an enterprise-ready investigation and rebuttal platform that replaces guesswork with a provable, 7-layer decision architecture:

```
[Relational Database (12 Tables)]
       ↓
[Supervised ML Risk Engine (XGBoost)] → [TreeSHAP Local Attribution]
       ↓
[7-Category Evidence Intelligence Engine] → [Quality & Consistency Scoring]
       ↓
[Grounded AI Response Engine] → [Deterministic Anti-Hallucination Guardrail]
       ↓
[Human-in-the-Loop Review Gate] → [Immutable Audit Trail]
```

---

## 3. Key Technical Highlights & Actual Project Results

### 1. Empirical Supervised Machine Learning
- We trained and evaluated an **XGBoost Classifier** on a strictly separated 15% held-out test partition ($N=150$).
- **Held-Out Test Results:** **83.8% Precision**, **63.8% Recall**, **0.724 F1 Score**, and **0.872 PR-AUC**.
- **Asymmetric Financial Optimization:** We calibrated the decision threshold to $\tau = 0.60$ by modeling the real business asymmetry between a $\$15$ false-positive arbitration penalty and a $\$489$ false-negative missed recovery.

### 2. Local TreeSHAP Explainability
- For every case, TreeSHAP attributes exact feature contributions (e.g. `+46.9%` from transaction amount, `+31.1%` from courier delivery acknowledgement), accompanied by an explicit compliance disclaimer: *"Model contribution — not causal proof."*

### 3. Zero-Hallucination Evidence Grounding
- Our **Grounding Validator** algorithmically verifies every citation against SQLite database records.
- If a delivery record is unconfirmed or missing, the AI is programmatically blocked from claiming fulfillment and is forced to output explicit missing evidence disclosures.
- Approval is strictly disabled if grounding validation fails.

### 4. Human-in-the-Loop & Immutable Auditability
- The system never auto-submits. A specialist can approve, edit and approve, reject, or request more evidence.
- Every single system, AI, and reviewer event is permanently logged with timestamps and actor IDs.

---

## 4. Responsible AI, Limitations & Future Roadmap

### Current Scope & Limitations
- **Synthetic Data:** Developed and tested on 1,000 synthetic records with realistic statistical distributions.
- **Offline Demo Mode:** Functions fully offline with deterministic fallback generation when external LLM API keys are unavailable.

### Future Roadmap
1. Multi-modal OCR evidence extraction from scanned courier bills of lading and paper invoices.
2. Direct REST webhook connectors for Shopify, Stripe, Adyen, and Braintree.
3. Active learning feedback loop to refine XGBoost decision thresholds on reviewer edits over time.
