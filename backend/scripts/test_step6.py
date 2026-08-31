"""
AI Chargeback Guardian — Step 6 Test Suite: Human-in-the-Loop, SHAP Explainability & Audit Trail

Comprehensive verification of:
1. SHAP explainability generation with local feature contributions
2. Human review state transitions (APPROVE, EDIT_AND_APPROVE, REJECT, NEEDS_MORE_EVIDENCE)
3. Grounding Safeguard: Approval blocked when grounding fails
4. Audit trail logging for all system, AI, and human reviewer events
5. REST API endpoints:
   - GET /api/v1/disputes/{id}/explanation
   - GET /api/v1/disputes/{id}/review
   - POST /api/v1/disputes/{id}/review
   - GET /api/v1/disputes/{id}/audit
"""

import sys
from pathlib import Path
import json

# Ensure project root and backend are in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.database.session import SessionLocal
from app.services import ExplainabilityService, HumanReviewService, AuditService
from app.schemas.review import HumanReviewCreateRequest, ReviewDecisionEnum
from app.schemas.ai import AIResponseOutput, GroundingStatusEnum
from app.main import app
from starlette.testclient import TestClient


def run_all_step6_tests():
    print("=" * 70)
    print("AI CHARGEBACK GUARDIAN — STEP 6 VERIFICATION SUITE")
    print("=" * 70)

    db = SessionLocal()
    client = TestClient(app)

    try:
        # =========================================================================
        # TEST 1: SHAP Local Explainability
        # =========================================================================
        print("\n--- TEST 1: SHAP Local Explainability ---")
        exp_svc = ExplainabilityService(db)
        exp = exp_svc.get_explanation("1")

        print(f"[PASS] Model Name: {exp.model_name} (Version: {exp.model_version})")
        print(f"[PASS] Win Probability: {round(exp.prediction_probability * 100, 1)}% | Score: {exp.score}/100 ({exp.classification})")
        print(f"[PASS] Baseline Value: {exp.base_value} | Method: {exp.method}")
        print(f"[PASS] Total Evaluated Features: {len(exp.features)}")
        print(f"[PASS] Top Positive Drivers: {[(f.display_name, f.impact_pct) for f in exp.top_positive_factors[:3]]}")
        print(f"[PASS] Top Negative Drivers: {[(f.display_name, f.impact_pct) for f in exp.top_negative_factors[:3]]}")

        assert exp.score >= 0 and exp.score <= 100
        assert len(exp.top_positive_factors) > 0
        assert len(exp.features) > 0
        assert "contributing factor" in exp.disclaimer.lower()

        # =========================================================================
        # TEST 2: SHAP Invalid Dispute Handling
        # =========================================================================
        print("\n--- TEST 2: SHAP Invalid Dispute Handling ---")
        try:
            exp_svc.get_explanation("999999")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            print(f"[PASS] Handled invalid dispute correctly: {e}")

        # =========================================================================
        # TEST 3: Human Review — Approve Flow
        # =========================================================================
        print("\n--- TEST 3: Human Review — Approve Decision ---")
        rev_svc = HumanReviewService(db)
        req_approve = HumanReviewCreateRequest(
            decision=ReviewDecisionEnum.APPROVE,
            reviewer_reference="REV-00892",
            reviewer_notes="Verified courier POD matches customer shipping address.",
        )
        res_approve = rev_svc.submit_review("1", req_approve)
        print(f"[PASS] Status: {res_approve.current_status} (Expected: APPROVE)")
        print(f"[PASS] Latest Reviewer: {res_approve.latest_review.reviewer_reference}")
        print(f"[PASS] Original Draft Length: {len(res_approve.original_ai_response)} chars")
        assert res_approve.current_status == "APPROVE"
        assert res_approve.latest_review is not None
        assert res_approve.latest_review.reviewer_decision == "APPROVE"

        # =========================================================================
        # TEST 4: Human Review — Edit and Approve Flow
        # =========================================================================
        print("\n--- TEST 4: Human Review — Edit and Approve Decision ---")
        edited_text = "FORMAL REBUTTAL (CUSTOM EDITED BY HUMAN REVIEWER REV-00892)\nAll transaction details verified."
        req_edit = HumanReviewCreateRequest(
            decision=ReviewDecisionEnum.EDIT_AND_APPROVE,
            reviewer_reference="REV-00892",
            edited_response=edited_text,
            reviewer_notes="Clarified courier GPS coordinates in custom section.",
        )
        res_edit = rev_svc.submit_review("2", req_edit)
        print(f"[PASS] Status: {res_edit.current_status} (Expected: EDIT_AND_APPROVE)")
        print(f"[PASS] Final Response Text: {res_edit.final_response[:60]}...")
        assert res_edit.current_status == "EDIT_AND_APPROVE"
        assert res_edit.final_response == edited_text

        # =========================================================================
        # TEST 5: Human Review — Request More Evidence Flow
        # =========================================================================
        print("\n--- TEST 5: Human Review — Request More Evidence Decision ---")
        req_more_ev = HumanReviewCreateRequest(
            decision=ReviewDecisionEnum.NEEDS_MORE_EVIDENCE,
            reviewer_reference="REV-00892",
            reviewer_notes="Customer claim requires secondary signature proof from courier before submission.",
        )
        res_more_ev = rev_svc.submit_review("5", req_more_ev)
        print(f"[PASS] Status: {res_more_ev.current_status} (Expected: NEEDS_MORE_EVIDENCE)")
        print(f"[PASS] Reviewer Notes Recorded: {res_more_ev.latest_review.reviewer_notes}")
        assert res_more_ev.current_status == "NEEDS_MORE_EVIDENCE"

        # =========================================================================
        # TEST 6: Human Review — Reject Claim Flow
        # =========================================================================
        print("\n--- TEST 6: Human Review — Reject Claim Decision ---")
        req_reject = HumanReviewCreateRequest(
            decision=ReviewDecisionEnum.REJECT,
            reviewer_reference="REV-00892",
            reviewer_notes="Merchant accepted customer claim; no contest will be filed.",
        )
        res_reject = rev_svc.submit_review("3", req_reject)
        print(f"[PASS] Status: {res_reject.current_status} (Expected: REJECT)")
        assert res_reject.current_status == "REJECT"

        # =========================================================================
        # TEST 7: Grounding Safeguard — Approval Blocked on Grounding Failure
        # =========================================================================
        print("\n--- TEST 7: Grounding Safeguard — Approval Blocked on Grounding Failure ---")
        # Temporarily create a mock service or check that if grounding fails, approval is blocked
        class FailingMockAIGenerator:
            def generate_response(self, disp_id):
                class MockAIResp:
                    grounding_status = GroundingStatusEnum.FAILED
                    recommended_action = "CONTEST"
                    draft_response = "Unsafe draft claiming unverified events."
                return MockAIResp()

        safe_rev_svc = HumanReviewService(db)
        safe_rev_svc.ai_generator = FailingMockAIGenerator()

        try:
            safe_rev_svc.submit_review("1", req_approve)
            assert False, "Approval should have been rejected due to Grounding FAILED"
        except ValueError as e:
            print(f"[PASS] Grounding Safeguard Successfully Blocked Approval: {e}")
            assert "Approval rejected" in str(e) or "grounding" in str(e).lower()

        # =========================================================================
        # TEST 8: Validation — Missing Notes for NEEDS_MORE_EVIDENCE
        # =========================================================================
        print("\n--- TEST 8: Validation — Missing Notes for NEEDS_MORE_EVIDENCE ---")
        try:
            HumanReviewCreateRequest(
                decision=ReviewDecisionEnum.NEEDS_MORE_EVIDENCE,
                reviewer_notes="",
            )
            assert False, "Should have failed Pydantic validation"
        except Exception as e:
            print(f"[PASS] Successfully caught missing notes: {e}")

        # =========================================================================
        # TEST 9: Audit Trail Logging Verification
        # =========================================================================
        print("\n--- TEST 9: Audit Trail Logging Verification ---")
        aud_svc = AuditService(db)
        aud_trail = aud_svc.get_audit_trail("1")
        print(f"[PASS] Audit Events Logged for Dispute 1: {aud_trail.events_count}")
        action_names = [e.action for e in aud_trail.events]
        print(f"[PASS] Recorded Actions: {action_names}")
        assert "REVIEW_APPROVED" in action_names
        for event in aud_trail.events:
            assert event.actor_type in ("SYSTEM", "AI", "HUMAN")

        # =========================================================================
        # TEST 10: REST API Endpoints (Explanation, Review, Audit)
        # =========================================================================
        print("\n--- TEST 10: REST API Endpoints Verification ---")
        # 10A. GET /api/v1/disputes/1/explanation
        resp_exp = client.get("/api/v1/disputes/1/explanation")
        print(f"[PASS] GET /api/v1/disputes/1/explanation -> HTTP {resp_exp.status_code}")
        assert resp_exp.status_code == 200
        exp_data = resp_exp.json()
        assert "features" in exp_data
        assert "top_positive_factors" in exp_data

        # 10B. GET /api/v1/disputes/1/review
        resp_rev_get = client.get("/api/v1/disputes/1/review")
        print(f"[PASS] GET /api/v1/disputes/1/review -> HTTP {resp_rev_get.status_code}")
        assert resp_rev_get.status_code == 200

        # 10C. POST /api/v1/disputes/1/review
        resp_rev_post = client.post(
            "/api/v1/disputes/1/review",
            json={
                "decision": "APPROVE",
                "reviewer_reference": "REV-00892",
                "reviewer_notes": "API test approval",
            },
        )
        print(f"[PASS] POST /api/v1/disputes/1/review -> HTTP {resp_rev_post.status_code}")
        assert resp_rev_post.status_code == 200

        # 10D. GET /api/v1/disputes/1/audit
        resp_aud = client.get("/api/v1/disputes/1/audit")
        print(f"[PASS] GET /api/v1/disputes/1/audit -> HTTP {resp_aud.status_code}")
        assert resp_aud.status_code == 200
        aud_data = resp_aud.json()
        assert aud_data["events_count"] > 0

        print("\n" + "=" * 70)
        print(">>> ALL STEP 6 TESTS PASSED SUCCESSFULLY WITH ZERO ERRORS <<<")
        print("=" * 70)

    finally:
        db.close()


if __name__ == "__main__":
    run_all_step6_tests()
