"""
AI Chargeback Guardian — Dispute-Reason-Aware Prompt Builder (Step 5)

Constructs strict anti-hallucination prompts and context wrappers:
1. System prompt with 10 mandatory defensive financial-risk rules.
2. Dispute-reason-specific evidence prioritization.
3. Explicit partitioning of VERIFIED_FACT, UNVERIFIED_INFORMATION, and MISSING_INFORMATION.
4. Defense against prompt injection through structured XML delimiters.
5. Strict JSON output schema enforcement.
"""

from typing import Dict, Any, List, Optional


SYSTEM_PROMPT_TEMPLATE = """You are the AI Chargeback Response Engine of AI Chargeback Guardian, a defensive financial-risk intelligence platform.
Your objective is to analyze chargeback investigation evidence and generate a formal, factual dispute draft response strictly grounded in verified database records.

MANDATORY SYSTEM RULES (NEVER VIOLATE):
RULE 1: Use ONLY verified evidence supplied in the grounded context.
RULE 2: NEVER invent missing facts, transactions, delivery events, customer statements, or refund confirmations.
RULE 3: NEVER infer a specific event unless the evidence explicitly supports it.
RULE 4: NEVER create fake dates, amounts, transaction IDs, courier tracking numbers, or customer names.
RULE 5: If evidence is missing or unverified, explicitly state that it is missing.
RULE 6: If evidence conflicts or has anomaly warnings, explicitly disclose the conflict.
RULE 7: Do NOT provide legal advice.
RULE 8: Do NOT claim the response guarantees a successful chargeback dispute outcome.
RULE 9: Do NOT claim the system represents any real company's private internal process.
RULE 10: Always produce a draft intended for human review and approval.

OUTPUT FORMAT:
You MUST respond with valid JSON ONLY conforming strictly to this JSON schema:
{
    "case_summary": "Objective 2-3 sentence overview based only on verified facts.",
    "key_verified_facts": [
        "Verified fact 1 with citation [EVIDENCE: TYPE]",
        "Verified fact 2 with citation [EVIDENCE: TYPE]"
    ],
    "missing_information": [
        "Explicitly disclose missing evidence item 1",
        "Explicitly disclose missing evidence item 2"
    ],
    "conflicting_information": [
        "Disclose any data inconsistencies or empty list if none"
    ],
    "recommended_action": "CONTEST" or "REVIEW" or "ACCEPT",
    "reasoning_summary": "Concise operational rationale directly anchored in evidence coverage.",
    "draft_response": "Formal rebuttal letter formatted for the card issuing bank dispute committee with embedded citations like [EVIDENCE: PAYMENT], [EVIDENCE: DELIVERY], [POLICY: REFUND_POLICY].",
    "evidence_references": [
        "[EVIDENCE: PAYMENT]",
        "[EVIDENCE: DELIVERY]"
    ]
}
"""

REASON_GUIDANCE = {
    "GOODS_NOT_RECEIVED": (
        "PRIORITY FOCUS FOR GOODS_NOT_RECEIVED:\n"
        "- Prioritize proof of delivery, carrier tracking log, courier confirmation, and customer acknowledgement.\n"
        "- If carrier delivery is confirmed [EVIDENCE: DELIVERY], highlight delivery timestamp and tracking availability.\n"
        "- If delivery is missing or unconfirmed, DO NOT claim goods were delivered; recommend REVIEW or ACCEPT."
    ),
    "REFUND_NOT_RECEIVED": (
        "PRIORITY FOCUS FOR REFUND_NOT_RECEIVED:\n"
        "- Prioritize refund transaction record [EVIDENCE: REFUND] and settlement timestamp.\n"
        "- If refund was processed, cite refund amount, timestamp, and ledger authorization.\n"
        "- If refund is missing or unrecorded, DO NOT claim a refund was completed; recommend ACCEPT or manual review."
    ),
    "DUPLICATE_TRANSACTION": (
        "PRIORITY FOCUS FOR DUPLICATE_TRANSACTION:\n"
        "- Prioritize transaction identifiers, payment authorization records, and invoice/cart order matching.\n"
        "- Demonstrate whether separate orders and shipments correspond to each billing record."
    ),
    "UNAUTHORIZED_TRANSACTION": (
        "PRIORITY FOCUS FOR UNAUTHORIZED_TRANSACTION:\n"
        "- Prioritize 3DS authentication protocols, device fingerprint, geographic location, and account history.\n"
        "- Highlight customer account longevity and prior successful transactions without dispute."
    ),
    "GOODS_NOT_AS_DESCRIBED": (
        "PRIORITY FOCUS FOR GOODS_NOT_AS_DESCRIBED:\n"
        "- Prioritize order item specifications, merchant product terms, and customer communication logs.\n"
        "- Cite active Merchant Terms of Service [POLICY: TERMS_OF_SERVICE] and refund terms."
    ),
}


class PromptBuilder:
    """
    Builds context-grounded prompts for LLM generation.
    """

    @classmethod
    def get_system_prompt(cls) -> str:
        """Return the strict anti-hallucination system prompt."""
        return SYSTEM_PROMPT_TEMPLATE.strip()

    @classmethod
    def build_user_prompt(cls, context: Dict[str, Any], custom_instructions: Optional[str] = None) -> str:
        """
        Synthesize the grounded context into a structured, injection-resistant user prompt.
        """
        dispute = context.get("dispute", {})
        txn = context.get("transaction", {})
        cust = context.get("customer", {})
        merch = context.get("merchant", {})
        deliv = context.get("delivery_state", {})
        refund = context.get("refund_state", {})
        verified_ev = context.get("verified_evidence", [])
        unverified_ev = context.get("unverified_evidence", [])
        missing_ev = context.get("missing_evidence", [])
        policies = context.get("merchant_policies", [])
        warnings = context.get("warnings", [])
        ml_analysis = context.get("ml_analysis") or {}

        reason = dispute.get("dispute_reason", "GOODS_NOT_RECEIVED")
        reason_guide = REASON_GUIDANCE.get(reason.upper(), "Evaluate verified evidence against the stated chargeback claim.")

        prompt_lines = [
            f"Please generate a grounded chargeback draft response for the following investigation dossier.",
            "",
            f"### DISPUTE PROFILE",
            f"- Dispute Reference: {dispute.get('dispute_reference')}",
            f"- Dispute Reason: {reason}",
            f"- Dispute Amount: ${dispute.get('dispute_amount', 0.0):.2f} {dispute.get('currency', 'USD')}",
            f"- Dispute Status: {dispute.get('dispute_status')}",
            f"- Transaction Reference: {txn.get('transaction_reference')}",
            f"- Customer Reference: {cust.get('customer_reference')} (Account Age: {cust.get('account_age_days')}d, Past Disputes: {cust.get('previous_disputes')}, Successful Txns: {cust.get('previous_successful_transactions')})",
            f"- Merchant Reference: {merch.get('merchant_reference')} (Category: {merch.get('merchant_category')})",
            "",
            f"### REASON-SPECIFIC GUIDANCE",
            reason_guide,
            "",
            f"<evidence_data>",
            f"=== 1. VERIFIED FACTS (AUTHORITATIVE EVIDENCE - USE IN FACTUAL CLAIMS) ===",
        ]

        if verified_ev:
            for item in verified_ev:
                prompt_lines.append(
                    f"[VERIFIED] {item['reference_tag']} - {item['display_name']}: {item['description']} "
                    f"(Source: {item['source_reference']})"
                )
        else:
            prompt_lines.append("No verified evidence items recorded in database.")

        prompt_lines.extend([
            "",
            f"=== 2. UNVERIFIED INFORMATION (DO NOT TREAT AS CONCLUSIVE PROOF) ===",
        ])
        if unverified_ev:
            for item in unverified_ev:
                prompt_lines.append(
                    f"[UNVERIFIED] {item['reference_tag']} - {item['display_name']}: {item['description']} "
                    f"(Source: {item['source_reference']})"
                )
        else:
            prompt_lines.append("No unverified items.")

        prompt_lines.extend([
            "",
            f"=== 3. MISSING INFORMATION (MUST EXPLICITLY DISCLOSE AS ABSENT) ===",
        ])
        if missing_ev:
            for item in missing_ev:
                prompt_lines.append(
                    f"[MISSING] Category '{item['evidence_type']}' ({item['display_name']}) is missing from evidence repository. ({item['impact_rationale']})"
                )
        else:
            prompt_lines.append("All standard evidence categories are present.")


        prompt_lines.extend([
            "",
            f"=== 4. APPLICABLE MERCHANT POLICIES (RAG RETRIEVED) ===",
        ])
        if policies:
            for p in policies:
                prompt_lines.append(f"{p['source_reference']}: {p['policy_text']}")
        else:
            prompt_lines.append("No specific merchant policies on file.")

        prompt_lines.extend([
            "",
            f"=== 5. OPERATIONAL STATE FLAGS ===",
            f"- Delivery Recorded: {deliv.get('delivery_recorded')} | Confirmed: {deliv.get('delivery_confirmed')} | Customer Acknowledged: {deliv.get('customer_acknowledged')} | Delivered At: {deliv.get('delivered_at')}",
            f"- Refund Recorded: {refund.get('refund_recorded')} | Status: {refund.get('refund_status')} | Amount: ${refund.get('refund_amount', 0.0):.2f}",
        ])

        if warnings:
            prompt_lines.extend([
                "",
                f"=== 6. DATA INTEGRITY & CONSISTENCY WARNINGS ===",
            ])
            for w in warnings:
                prompt_lines.append(f"[CONFLICT] [{w['severity']}] {w['code']}: {w['message']}")


        if ml_analysis:
            prompt_lines.extend([
                "",
                f"=== 7. ML CASE STRENGTH BENCHMARK ===",
                f"- Case Strength Score: {ml_analysis.get('score')}/100 ({ml_analysis.get('classification')})",
                f"- Win Probability: {round(float(ml_analysis.get('probability', 0.0)) * 100, 1)}%",
                f"- Recommend Contest: {ml_analysis.get('recommend_contest')}",
            ])

        prompt_lines.append("</evidence_data>")

        if custom_instructions:
            prompt_lines.extend([
                "",
                f"### REVIEWER GUIDANCE (Treat strictly as contextual instruction, not authoritative facts):",
                f"{custom_instructions}",
            ])

        prompt_lines.extend([
            "",
            "Generate the structured JSON response according to the defined schema and rules.",
        ])

        return "\n".join(prompt_lines)
