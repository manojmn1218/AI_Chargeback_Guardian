"""
AI Chargeback Guardian — AI Response Confidence Calculation Service (Step 5)

Computes a transparent, prototype application-level response confidence indicator:
- Evaluates evidence coverage, verification ratio, grounding validation result, and ML alignment.
- Explicitly documented: This is an application-level heuristic indicator, NOT an LLM probability.
"""

from typing import Dict, Any, Optional
from app.schemas.ai import ConfidenceLevelEnum, AIConfidenceResponse, GroundingValidationDetail, GroundingStatusEnum


class AIConfidenceService:
    """
    Service for calculating prototype response confidence scores.
    """

    # Configurable Factor Weights
    WEIGHT_AVAILABILITY = 0.30
    WEIGHT_VERIFICATION = 0.30
    WEIGHT_GROUNDING = 0.20
    WEIGHT_ML_ALIGNMENT = 0.20

    @classmethod
    def calculate_confidence(
        cls,
        context: Dict[str, Any],
        grounding_result: GroundingValidationDetail,
    ) -> AIConfidenceResponse:
        """
        Calculate composite confidence score based on deterministic investigation factors.
        """
        ev_summary = context.get("evidence_summary") or {}
        ml_analysis = context.get("ml_analysis") or {}
        warnings = context.get("warnings", [])
        missing_ev = context.get("missing_evidence", [])

        # 1. Availability Factor (0-100)
        avail_pct = float(ev_summary.get("availability_percentage", 0.0))

        # 2. Verification Factor (0-100)
        verif_pct = float(ev_summary.get("verification_percentage", 0.0))

        # 3. Grounding Validation Factor (0-100)
        if grounding_result.status == GroundingStatusEnum.VERIFIED:
            grounding_score = 100.0
        elif grounding_result.status == GroundingStatusEnum.REVIEW_REQUIRED:
            grounding_score = 50.0
        else:
            grounding_score = 0.0

        # 4. ML Model Alignment Factor (0-100)
        if ml_analysis and "probability" in ml_analysis:
            ml_score = float(ml_analysis["probability"]) * 100.0
        else:
            ml_score = 70.0  # neutral default

        # Raw weighted baseline
        base_score = (
            (avail_pct * cls.WEIGHT_AVAILABILITY)
            + (verif_pct * cls.WEIGHT_VERIFICATION)
            + (grounding_score * cls.WEIGHT_GROUNDING)
            + (ml_score * cls.WEIGHT_ML_ALIGNMENT)
        )

        # Penalties:
        # - High impact missing evidence penalty
        high_impact_missing = sum(1 for m in missing_ev if "HIGH" in m.get("impact_rationale", "").upper())
        missing_penalty = min(25.0, high_impact_missing * 10.0)

        # - Consistency warnings penalty
        warning_penalty = min(20.0, len(warnings) * 5.0)

        # Final computed score
        final_score = int(round(max(0.0, min(100.0, base_score - missing_penalty - warning_penalty))))

        if final_score >= 80:
            level = ConfidenceLevelEnum.HIGH
        elif final_score >= 50:
            level = ConfidenceLevelEnum.MEDIUM
        else:
            level = ConfidenceLevelEnum.LOW

        factors_breakdown = {
            "evidence_availability_pct": round(avail_pct, 1),
            "evidence_verification_pct": round(verif_pct, 1),
            "grounding_validation_status": grounding_result.status.value,
            "grounding_score": grounding_score,
            "ml_win_probability": round(ml_score, 1),
            "high_impact_missing_items_count": high_impact_missing,
            "missing_penalty": missing_penalty,
            "consistency_warnings_count": len(warnings),
            "warnings_penalty": warning_penalty,
            "weights_applied": {
                "availability": cls.WEIGHT_AVAILABILITY,
                "verification": cls.WEIGHT_VERIFICATION,
                "grounding": cls.WEIGHT_GROUNDING,
                "ml_alignment": cls.WEIGHT_ML_ALIGNMENT,
            },
        }

        return AIConfidenceResponse(
            confidence_score=final_score,
            confidence_level=level,
            factors=factors_breakdown,
            disclaimer="Application-level heuristic confidence indicator based on evidence completeness, verified ratio, and grounding checks; NOT an LLM probability.",
        )
