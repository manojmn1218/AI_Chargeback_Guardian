"""
AI Chargeback Guardian — Response Generation Orchestrator (Step 5)

Orchestrates the complete evidence-grounded AI generation pipeline:
1. Gathers relational dispute records, ML predictions, and evidence intelligence.
2. Constructs injection-resistant, reason-aware grounded prompt.
3. Invokes LLM provider (or deterministic fallback engine).
4. Validates structured JSON schema with Pydantic.
5. Executes deterministic anti-hallucination grounding validation.
6. Computes transparent application response confidence.
7. Packages comprehensive AI investigation summary.
"""

import json
import re
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models import Dispute
from app.schemas.ai import (
    AIResponseOutput,
    AIInvestigationSummaryResponse,
    AIResponseGenerateRequest,
    GroundingStatusEnum,
)
from app.services.ai.llm_service import LLMProvider, DemoLLMProvider, get_llm_provider
from app.services.ai.grounding_service import EvidenceGroundingService
from app.services.ai.prompt_builder import PromptBuilder
from app.services.ai.grounding_validator import GroundingValidator
from app.services.ai.confidence_service import AIConfidenceService
from app.services.evidence_service import EvidenceService


def parse_and_sanitize_json(raw_text: str) -> Dict[str, Any]:
    """
    Extract and parse JSON object from LLM response text.
    Handles potential markdown fences like ```json ... ```.
    """
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        # Strip code block fences
        cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned)
        cleaned = re.sub(r"\n?```$", "", cleaned)
        cleaned = cleaned.strip()

    # Find outermost JSON object
    match = re.search(r"(\{.*\})", cleaned, flags=re.DOTALL)
    if match:
        cleaned = match.group(1)

    return json.loads(cleaned)


class AIResponseGenerator:
    """
    Main entry point for generating grounded chargeback investigation drafts.
    """

    def __init__(self, db: Session, llm_provider: Optional[LLMProvider] = None):
        self.db = db
        self.grounding_service = EvidenceGroundingService(db)
        self.evidence_service = EvidenceService(db)
        self.llm_provider = llm_provider or get_llm_provider()

    def generate_response(
        self,
        dispute_ref_or_id: str,
        request: Optional[AIResponseGenerateRequest] = None,
    ) -> AIInvestigationSummaryResponse:
        """
        Execute full end-to-end grounded generation workflow.
        """
        request = request or AIResponseGenerateRequest()

        # 1. Build Grounded Context
        context = self.grounding_service.build_grounded_context(dispute_ref_or_id)
        dispute_info = context["dispute"]
        dispute_id = dispute_info["id"]
        dispute_ref = dispute_info["dispute_reference"]
        dispute_reason = dispute_info["dispute_reason"]

        # 2. Build Prompts
        system_prompt = PromptBuilder.get_system_prompt()
        user_prompt = PromptBuilder.build_user_prompt(
            context=context,
            custom_instructions=request.custom_instructions,
        )

        # 3. Generate from LLM Provider (with graceful fallback on failure)
        raw_output = ""
        is_fallback = self.llm_provider.is_fallback
        provider_name = getattr(self.llm_provider, "provider_name", "demo")
        model_name = getattr(self.llm_provider, "model", None)

        try:
            raw_output = self.llm_provider.generate(user_prompt, system_prompt)
            data_dict = parse_and_sanitize_json(raw_output)
            ai_output = AIResponseOutput.model_validate(data_dict)
        except Exception as e:
            logger.warning(f"Primary LLM generation or parsing failed ({e}). Falling back to DemoLLMProvider.")
            fallback_provider = DemoLLMProvider()
            raw_output = fallback_provider.generate(user_prompt, system_prompt)
            data_dict = parse_and_sanitize_json(raw_output)
            ai_output = AIResponseOutput.model_validate(data_dict)
            is_fallback = True
            provider_name = "demo"
            model_name = "deterministic_fallback"

        # 4. Deterministic Grounding Validation
        grounding_result = GroundingValidator.validate(ai_output, context)

        # 5. Prototype Response Confidence Calculation
        confidence_result = AIConfidenceService.calculate_confidence(context, grounding_result)

        # 6. Save Draft to Dispute Record in SQLite (does NOT finalize/approve)
        try:
            db_dispute = self.db.query(Dispute).filter(Dispute.id == dispute_id).first()
            if db_dispute:
                db_dispute.ai_response_draft = ai_output.draft_response
                db_dispute.recommendation = ai_output.recommended_action.lower()
                self.db.commit()
        except Exception as e:
            logger.error(f"Failed to persist draft in dispute table: {e}")
            self.db.rollback()

        # 7. Assemble Full Investigation Dossier
        full_investigation = self.evidence_service.get_investigation(dispute_ref_or_id)

        # Extract structured warnings
        warnings_list = full_investigation.warnings or []

        return AIInvestigationSummaryResponse(
            dispute_id=dispute_id,
            dispute_reference=dispute_ref,
            dispute_reason=dispute_reason,
            case_summary=ai_output.case_summary,
            ml_analysis=full_investigation.ml_analysis,
            evidence_summary=full_investigation.evidence_analysis,
            key_verified_facts=ai_output.key_verified_facts,
            missing_information=ai_output.missing_information,
            conflicting_information=ai_output.conflicting_information,
            warnings=warnings_list,
            recommended_action=ai_output.recommended_action,
            reasoning_summary=ai_output.reasoning_summary,
            draft_response=ai_output.draft_response,
            evidence_references=ai_output.evidence_references,
            grounding_status=grounding_result.status,
            grounding_details=grounding_result,
            confidence=confidence_result,
            provider=provider_name,
            model=model_name,
            is_fallback=is_fallback,
            generated_at=datetime.utcnow(),
        )
