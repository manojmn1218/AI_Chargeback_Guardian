# AI Chargeback Guardian — Evidence-Grounded AI Response Engine (Step 5)

## Overview & Core Philosophy

The **AI Response Engine** is a specialized, defensive financial-risk intelligence subsystem designed to analyze chargeback investigation dossiers and generate authoritative, formal dispute contest drafts.

### Fundamental Operating Principles:
1. **The LLM is a Drafting Component**: The language model acts exclusively as an evidentiary synthesizer and formal drafter. It does **not** make binding legal or arbitration commitments.
2. **Database as Immutable Source of Truth**: Every factual claim, event timestamp, financial sum, and reference cited in generated responses must strictly originate from verified SQLite relational database records.
3. **Zero Hallucination Tolerance**: If evidence is absent, unconfirmed, or conflicting, the system explicitly discloses the gap and prohibits affirmative claims.
4. **Mandatory Human-in-the-Loop**: All generated drafts are presented for human review and edit. No draft is automatically dispatched or finalized without human reviewer authorization.

---

## System Architecture

```
+----------------------------------------------------------------------------------------------------+
|                                      DISPUTE INVESTIGATION INPUT                                   |
|                        (Dispute, Transaction, Customer, Merchant, Delivery, Refund)                |
+----------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                                    STEP 4 EVIDENCE ENGINE SERVICE                                  |
|   - 7 Standard Categories Completeness (Availability % & Verification %)                           |
|   - Deterministic Quality Scoring (0-100) & Dispute-Reason-Aware Relevance Ranking                 |
|   - Chronological Timeline Synthesis & Consistency Anomaly Warnings                                |
+----------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                                 EVIDENCE GROUNDING SERVICE (Step 5)                                |
|   1. Partitions Data: [VERIFIED_FACT] vs [UNVERIFIED_INFORMATION] vs [MISSING_INFORMATION]        |
|   2. Merchant Policy RAG Retrieval: Terms of Service, Refund Policy, Shipping Policy               |
|   3. Prompt Injection Defense: Strips delimiters, command overrides & untrusted tags               |
|   4. Generates Immutable Grounded Context Payload                                                  |
+----------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                                       PROMPT BUILDER (Step 5)                                      |
|   - Enforces 10 Strict Anti-Hallucination System Rules                                             |
|   - Reason-Aware Evidentiary Guidance (GOODS_NOT_RECEIVED, REFUND_NOT_RECEIVED, etc.)              |
|   - Schema Contract: Strict JSON output with traceable [EVIDENCE: ...] & [POLICY: ...] tags       |
+----------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                                      LLM PROVIDER ABSTRACTION                                      |
|          +--------------------------------------+  +-------------------------------------+         |
|          |     API Provider (OpenAI / HTTP)     |  |   Deterministic Demo/Fallback Mode  |         |
|          | (Invoked when API Key is configured) |  |   (Zero API key, offline fallback)  |         |
|          +--------------------------------------+  +-------------------------------------+         |
+----------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                                    GROUNDING VALIDATOR SERVICE                                     |
|   - Deterministic Citation Existence Check (verifies [EVIDENCE: ...] tags exist in DB)             |
|   - Dispute Ownership Check (verifies items belong to specific dispute)                            |
|   - Unsupported Delivery Claim Check (fails if delivery_confirmed=False & delivery claimed)       |
|   - Unsupported Refund Claim Check (fails if refund missing & refund processed claimed)           |
|   - Unsupported Customer Ack Check (fails if customer_acknowledged=False & ack claimed)           |
|   - Status Assigned: VERIFIED | REVIEW_REQUIRED | FAILED                                           |
+----------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                                       CONFIDENCE SERVICE                                           |
|   - Transparent Heuristic Calculation: Coverage (30%), Verification (30%), Grounding (20%), ML(20%)|
|   - Penalties: High-Impact Missing Items (-10 pts) & Consistency Warnings (-5 pts)                 |
|   - Output: Score (0-100), Level (HIGH, MEDIUM, LOW), Factor Breakdown                             |
+----------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                             FRONTEND AI RESPONSE PANEL & HUMAN GATE                                |
|   - Interactive Reviewer Interface (Copy, Live Edit Mode, Regenerate)                              |
|   - Traceable Evidence Citation Badges & Grounding Validation Accordion                            |
|   - Clear Mode Badge: Demo Deterministic Engine vs External LLM API Provider                       |
+----------------------------------------------------------------------------------------------------+
```

---

## 1. LLM Provider Abstraction

The system adopts a modular provider architecture located at `backend/app/services/ai/llm_service.py`:

- **`LLMProvider` (ABC)**: Defines the common interface `generate(prompt, system_prompt, temperature) -> str`.
- **`APILLMProvider`**: Calls standard OpenAI-compatible `/chat/completions` endpoints over HTTP using `httpx`. Secrets are read exclusively from environment variables (`LLM_API_KEY`, `LLM_PROVIDER`, `LLM_MODEL`).
- **`DemoLLMProvider`**: A robust, deterministic, rule-based response generator that produces complete structured JSON responses directly from verified SQLite records without requiring an API key or internet access.
- **`get_llm_provider()`**: Factory function that inspects environment configuration. If `LLM_API_KEY` is empty, it automatically defaults to `DemoLLMProvider`.

---

## 2. Evidence Grounding & Partitioning

Located at `backend/app/services/ai/grounding_service.py`:

1. **Strict Partitioning**:
   - `VERIFIED_FACT`: Items where `available == True` and `verified == True` from authoritative sources.
   - `UNVERIFIED_INFORMATION`: Items present in the database but lacking cryptographic/third-party verification.
   - `MISSING_INFORMATION`: Items where `available == False` or status is `MISSING`.
2. **Explicit Labeling**: The grounded context explicitly informs the model which items may be stated as fact and which items must be disclosed as missing.
3. **State Ingestion**: Ingests boolean state flags (`delivery_confirmed`, `customer_acknowledged`, `tracking_available`, `refund_status`) directly from relational database tables.

---

## 3. Merchant Policy Retrieval (RAG Layer)

The grounding service includes a lightweight retrieval layer for merchant terms and operating policies:
- Queries active records from the `merchant_policies` table for the dispute's merchant ID.
- Applies dispute-reason relevance filtering:
  - `GOODS_NOT_RECEIVED`: Prioritizes `SHIPPING_POLICY`, `TERMS_OF_SERVICE`, `REFUND_POLICY`.
  - `REFUND_NOT_RECEIVED`: Prioritizes `REFUND_POLICY`, `CANCELLATION_POLICY`, `TERMS_OF_SERVICE`.
  - `GOODS_NOT_AS_DESCRIBED`: Prioritizes `TERMS_OF_SERVICE`, `REFUND_POLICY`.
  - `DUPLICATE_TRANSACTION`: Prioritizes `TERMS_OF_SERVICE`, `REFUND_POLICY`.
  - `UNAUTHORIZED_TRANSACTION`: Prioritizes `TERMS_OF_SERVICE`.
- Generates policy source citations (e.g., `[POLICY: REFUND_POLICY]`).

---

## 4. Dispute-Reason-Aware Prompt Construction

Located at `backend/app/services/ai/prompt_builder.py`:

### 10 Mandatory System Prompt Rules:
1. **Rule 1**: Use only verified evidence supplied in the context.
2. **Rule 2**: Never invent missing facts.
3. **Rule 3**: Never infer a specific event unless explicitly supported by evidence.
4. **Rule 4**: Never create fake dates, amounts, transaction IDs, courier numbers, or customer names.
5. **Rule 5**: If evidence is missing, explicitly disclose that it is missing.
6. **Rule 6**: If evidence conflicts, explicitly disclose the conflict.
7. **Rule 7**: Do not provide legal advice.
8. **Rule 8**: Do not claim the response guarantees a successful arbitration outcome.
9. **Rule 9**: Do not claim the system represents any real company's private internal process.
10. **Rule 10**: Produce a draft intended for human review.

---

## 5. Structured JSON Output Contract

The LLM is prompted to return valid JSON conforming to the Pydantic schema `AIResponseOutput`:

```json
{
  "case_summary": "Objective 2-3 sentence overview based only on verified facts.",
  "key_verified_facts": [
    "Transaction TXN-005068 was authenticated via 3DS 2.0 [EVIDENCE: PAYMENT].",
    "Carrier Fedex confirmed signed delivery with GPS coordinates [EVIDENCE: DELIVERY]."
  ],
  "missing_information": [
    "Refund record is missing from merchant settlement ledger."
  ],
  "conflicting_information": [],
  "recommended_action": "CONTEST",
  "reasoning_summary": "Carrier proof of delivery and 3DS authorization logs provide strong contest basis.",
  "draft_response": "Formal rebuttal letter formatted for issuing bank arbitration committee...",
  "evidence_references": [
    "[EVIDENCE: PAYMENT]",
    "[EVIDENCE: DELIVERY]",
    "[POLICY: SHIPPING_POLICY]"
  ]
}
```

---

## 6. Deterministic Grounding Validation

Located at `backend/app/services/ai/grounding_validator.py`:

To guarantee zero hallucinated claims, every generated output undergoes automated deterministic validation checks:
1. **Evidence Reference Existence Check**: Verifies that every cited `[EVIDENCE: ...]` and `[POLICY: ...]` tag exists in the dispute's actual verified evidence list.
2. **Unsupported Delivery Claim Check**: If `delivery_confirmed == False` in the database, the validator scans the draft for phrases like *"delivery was confirmed"* or *"delivered successfully"*. If found, it triggers `GroundingStatus = FAILED`.
3. **Unsupported Refund Claim Check**: If no processed refund exists in the database, claims like *"refund was processed"* trigger `GroundingStatus = FAILED`.
4. **Unsupported Customer Acknowledgement Check**: If `customer_acknowledged == False`, claiming the customer confirmed receipt fails grounding.
5. **Missing Evidence Distinction**: Verifies that missing items are not cited as verified proof.

---

## 7. Transparent Confidence Calculation

Located at `backend/app/services/ai/confidence_service.py`:

Computes a composite application-level heuristic confidence indicator (0 to 100):
- **Evidence Availability Coverage (30% weight)**: `(available_count / 7) * 30`
- **Evidence Verification Ratio (30% weight)**: `(verified_count / 7) * 30`
- **Grounding Validation Outcome (20% weight)**: 100 for `VERIFIED`, 50 for `REVIEW_REQUIRED`, 0 for `FAILED`
- **ML Win Probability Alignment (20% weight)**: Step 3 XGBoost win probability scaled to 100
- **Penalties**:
  - High-impact missing evidence items: -10 points per item (max -25)
  - Consistency warnings / anomalies: -5 points per warning (max -20)
- **Levels**:
  - `HIGH`: Score >= 80
  - `MEDIUM`: Score 50 - 79
  - `LOW`: Score < 50

*Disclaimer*: Clearly documented in the UI and API response that this is an application-level heuristic indicator based on database completeness and grounding checks, **not** an LLM probability.

---

## 8. Fallback Demo Mode

When no LLM API key is configured or when external APIs are unreachable:
- The system activates `DemoLLMProvider`.
- Clearly displays `Demo Mode — Deterministic Rebuttal Engine (No External LLM API Key Configured)` in the UI and sets `is_fallback: true` in the API payload.
- Generates a complete, evidence-grounded rebuttal letter formatted with actual database values.

---

## 9. Security & Anti-Prompt-Injection Defenses

- **Environment Isolation**: API keys and secrets are loaded via `pydantic-settings` from `.env` and masked in all log outputs.
- **Untrusted Content Sanitization**: Database evidence descriptions and user text are sanitized using regex filtering to neutralize delimiter escapes (e.g. `</evidence_data>`) and instruction overrides (e.g. `ignore previous instructions`).
- **Data Encapsulation**: Relational evidence records are enclosed within `<evidence_data>` delimiter blocks and treated purely as inert data tokens.
- **No Real Customer PII**: Synthetic data only (`CUST-000001`, `MER-000001`, `DEV-000123`).

---

## 10. Limitations & Boundaries

1. **Synthetic Simulation**: Built for defensive risk prototype evaluation using synthetic SQLite records.
2. **Drafting Scope**: The engine generates drafts; final contest submission and arbitration decisions require human reviewer approval (implemented in Step 6).
3. **Card Scheme Rule Variations**: Prototype heuristics model general card network contest principles (Visa/Mastercard 3DS, signed POD, ledger audit trails) but do not replace specialized arbitration counsel.
