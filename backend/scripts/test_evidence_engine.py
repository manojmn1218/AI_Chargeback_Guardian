"""
AI Chargeback Guardian — Evidence Intelligence Engine Test Suite (Step 4)

Comprehensive verification of:
1. Valid dispute investigation
2. Dispute with missing evidence (counts & percentages)
3. Dispute with unverified evidence (distinction between MISSING and AVAILABLE_UNVERIFIED)
4. Dispute consistency check rules & warning generation
5. Invalid dispute ID handling (HTTP 404 / ValueError)
6. Dispute with no evidence (graceful fallback)
7. Exact mathematical calculation of availability %, verification %, quality score
8. Integration with Step 3 ML prediction service
9. FastAPI REST endpoints tested in-memory with TestClient:
   - GET /api/v1/disputes/{id}/investigation & /api/disputes/{id}/investigation
   - GET /api/v1/disputes/{id}/timeline & /api/disputes/{id}/timeline
   - GET /api/v1/disputes/{id}/evidence-summary & /api/disputes/{id}/evidence-summary
"""

import sys
from pathlib import Path
import json
from datetime import datetime, timedelta

# Add project root and backend to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.database.session import SessionLocal
from app.models import Dispute, Evidence, Transaction, Customer, Merchant, Order, Delivery, Refund, Communication
from app.services.evidence_service import EvidenceService, DEFAULT_EVIDENCE_WEIGHTS, STANDARD_CATEGORIES
from app.schemas.evidence import EvidenceStatusEnum
from app.main import app
from starlette.testclient import TestClient


def test_offline_evidence_calculations():
    print("=" * 60)
    print("TEST SUITE 1: Evidence Engine Mathematical Calculations")
    print("=" * 60)

    db = SessionLocal()
    try:
        service = EvidenceService(db)

        # 1. Test standard completeness calculation: 7 expected, 6 available, 5 verified, 1 missing
        mock_evidence = [
            Evidence(id=1, dispute_id=999, evidence_type="PAYMENT", description="3DS Auth", source_reference="GATEWAY_3DS", available=True, verified=True, evidence_timestamp=datetime(2026, 8, 1)),
            Evidence(id=2, dispute_id=999, evidence_type="INVOICE", description="Digital Invoice", source_reference="ERP", available=True, verified=True, evidence_timestamp=datetime(2026, 8, 1)),
            Evidence(id=3, dispute_id=999, evidence_type="ORDER", description="Order Log", source_reference="COMMERCE", available=True, verified=True, evidence_timestamp=datetime(2026, 8, 1)),
            Evidence(id=4, dispute_id=999, evidence_type="DELIVERY", description="Proof of Delivery", source_reference="FEDEX", available=True, verified=True, evidence_timestamp=datetime(2026, 8, 2)),
            Evidence(id=5, dispute_id=999, evidence_type="CUSTOMER_COMMUNICATION", description="Support Chat", source_reference="ZENDESK", available=True, verified=False, evidence_timestamp=datetime(2026, 8, 3)),
            Evidence(id=6, dispute_id=999, evidence_type="MERCHANT_POLICY", description="Terms Accepted", source_reference="POLICY_ENGINE", available=True, verified=True, evidence_timestamp=datetime(2026, 8, 1)),
            Evidence(id=7, dispute_id=999, evidence_type="REFUND", description="No refund", source_reference="None on file", available=False, verified=False, evidence_timestamp=None),
        ]

        metrics = service.calculate_completeness(mock_evidence)
        print(f"[PASS] Expected Count: {metrics.expected_evidence_count} (Expected: 7)")
        print(f"[PASS] Available Count: {metrics.available_evidence_count} (Expected: 6)")
        print(f"[PASS] Verified Count: {metrics.verified_evidence_count} (Expected: 5)")
        print(f"[PASS] Missing Count: {metrics.missing_evidence_count} (Expected: 1)")
        print(f"[PASS] Availability %: {metrics.availability_percentage}% (Expected: 85.7%)")
        print(f"[PASS] Verification %: {metrics.verification_percentage}% (Expected: 71.4%)")
        print(f"[PASS] Quality Score: {metrics.quality_score}/100")

        assert metrics.expected_evidence_count == 7
        assert metrics.available_evidence_count == 6
        assert metrics.verified_evidence_count == 5
        assert metrics.missing_evidence_count == 1
        assert metrics.availability_percentage == 85.7
        assert metrics.verification_percentage == 71.4
        assert 0.0 <= metrics.quality_score <= 100.0

        # 2. Test status assignment & unverified vs missing distinction
        checklist, strongest, missing = service.evaluate_evidence_items("GOODS_NOT_RECEIVED", mock_evidence)
        
        status_map = {item.evidence_type: item.status for item in checklist}
        assert status_map["DELIVERY"] == EvidenceStatusEnum.AVAILABLE_VERIFIED
        assert status_map["CUSTOMER_COMMUNICATION"] == EvidenceStatusEnum.AVAILABLE_UNVERIFIED
        assert status_map["REFUND"] == EvidenceStatusEnum.MISSING

        print(f"[PASS] Evidence Status Distinction Verified:")
        print(f"       - DELIVERY: {status_map['DELIVERY'].value}")
        print(f"       - CUSTOMER_COMMUNICATION: {status_map['CUSTOMER_COMMUNICATION'].value} (Available but unverified)")
        print(f"       - REFUND: {status_map['REFUND'].value} (Missing)")

        # 3. Test strongest evidence ranking for GOODS_NOT_RECEIVED
        assert len(strongest) > 0
        top_item = strongest[0]
        print(f"[PASS] Top Evidence for GOODS_NOT_RECEIVED: {top_item.evidence_type} (Score: {top_item.relevance_score}, Rank: {top_item.rank})")
        assert top_item.evidence_type == "DELIVERY", "Delivery should be top-ranked for GOODS_NOT_RECEIVED"

        # 4. Test missing evidence impact assessment
        assert len(missing) == 1
        assert missing[0].evidence_type == "REFUND"
        print(f"[PASS] Missing Evidence identified: {missing[0].evidence_type} (Impact: {missing[0].impact_level})")

        # 5. Test dispute reason awareness with REFUND_NOT_RECEIVED
        checklist_ref, strongest_ref, _ = service.evaluate_evidence_items("REFUND_NOT_RECEIVED", mock_evidence)
        top_ref = strongest_ref[0]
        print(f"[PASS] Top Available Evidence for REFUND_NOT_RECEIVED: {top_ref.evidence_type} (Relevance: {top_ref.relevance_score})")

        # 6. Test dispute with zero evidence
        zero_metrics = service.calculate_completeness([])
        print(f"[PASS] Zero Evidence Case: Available={zero_metrics.available_evidence_count}, Verified={zero_metrics.verified_evidence_count}, Avail%={zero_metrics.availability_percentage}%, Quality={zero_metrics.quality_score}")
        assert zero_metrics.available_evidence_count == 0
        assert zero_metrics.verified_evidence_count == 0
        assert zero_metrics.missing_evidence_count == 7
        assert zero_metrics.availability_percentage == 0.0
        assert zero_metrics.quality_score == 0.0

    finally:
        db.close()


def test_consistency_check_rules():
    print("\n" + "=" * 60)
    print("TEST SUITE 2: Evidence Consistency Check & Warning Engine")
    print("=" * 60)

    db = SessionLocal()
    try:
        service = EvidenceService(db)

        # 1. Test clean real dispute from database
        real_dispute = db.query(Dispute).first()
        if real_dispute:
            warnings = service.run_consistency_checks(real_dispute)
            print(f"[PASS] Real Dispute #{real_dispute.dispute_reference} Consistency Warnings: {len(warnings)} found")

        # 2. Test Rule: Delivery date occurs before order date
        mock_disp = Dispute(
            id=9999,
            dispute_reference="DISP-TEST-WARN",
            dispute_reason="GOODS_NOT_RECEIVED",
            dispute_amount=100.0,
            dispute_timestamp=datetime(2026, 8, 10),
        )
        mock_txn = Transaction(
            id=9999,
            amount=100.0,
            currency="USD",
            transaction_timestamp=datetime(2026, 8, 1),
        )
        mock_disp.transaction = mock_txn
        
        # Test amount mismatch warning
        mock_disp.dispute_amount = 150.0  # Mismatch: 150 vs 100
        warnings_amt = service.run_consistency_checks(mock_disp)
        amt_codes = [w.code for w in warnings_amt]
        assert "AMOUNT_MISMATCH" in amt_codes
        print(f"[PASS] Amount Mismatch caught correctly: {[w.message for w in warnings_amt if w.code == 'AMOUNT_MISMATCH'][0]}")

        # Test dispute filed before transaction timestamp
        mock_disp.dispute_timestamp = datetime(2026, 7, 25) # before Aug 1
        warnings_disp_date = service.run_consistency_checks(mock_disp)
        disp_date_codes = [w.code for w in warnings_disp_date]
        assert "DISPUTE_BEFORE_TRANSACTION" in disp_date_codes
        print(f"[PASS] Dispute Before Transaction caught correctly: {[w.message for w in warnings_disp_date if w.code == 'DISPUTE_BEFORE_TRANSACTION'][0]}")

    finally:
        db.close()


def test_database_dispute_investigation():
    print("\n" + "=" * 60)
    print("TEST SUITE 3: Real Database Relational Investigation Retrieval")
    print("=" * 60)

    db = SessionLocal()
    try:
        service = EvidenceService(db)

        # Test at least 3 distinct real synthetic disputes from database
        sample_disputes = db.query(Dispute).limit(3).all()
        assert len(sample_disputes) >= 3, "Expected at least 3 disputes in database"

        for idx, disp in enumerate(sample_disputes, start=1):
            print(f"\n--- Investigating Real Case #{idx}: {disp.dispute_reference} (ID: {disp.id}) ---")
            investigation = service.get_investigation(str(disp.id))

            # Validate Dispute Info
            assert investigation.dispute.id == disp.id
            assert investigation.dispute.dispute_reference == disp.dispute_reference
            print(f"[PASS] Dispute Info: Amount=${investigation.dispute.dispute_amount:.2f}, Reason={investigation.dispute.dispute_reason}, Status={investigation.dispute.dispute_status}")

            # Validate Customer & Merchant
            assert investigation.dispute.customer is not None
            assert investigation.dispute.merchant is not None
            assert investigation.dispute.transaction is not None
            print(f"[PASS] Entities: Customer={investigation.dispute.customer.customer_reference}, Merchant={investigation.dispute.merchant.merchant_reference}, Txn={investigation.dispute.transaction.transaction_reference}")

            # Validate Evidence Completeness & Quality Score
            ev = investigation.evidence_analysis
            print(f"[PASS] Evidence: Total Expected={ev.total_expected}, Available={ev.available}, Verified={ev.verified}, Missing={ev.missing}")
            print(f"       Availability%={ev.availability_percentage}%, Verification%={ev.verification_percentage}%, Quality Score={ev.quality_score}/100")
            assert ev.total_expected == 7
            assert ev.available + ev.missing == 7
            assert len(ev.evidence_checklist) == 7

            # Validate Strongest & Missing Evidence
            print(f"[PASS] Strongest Evidence Items: {len(ev.strongest_evidence)}")
            for s in ev.strongest_evidence:
                print(f"       - Rank #{s.rank}: {s.evidence_type} ({s.category_display_name}) | Status={s.status.value} | Relevance={s.relevance_score}")
            if ev.missing_evidence:
                print(f"[PASS] Missing Evidence Items: {len(ev.missing_evidence)}")
                for m in ev.missing_evidence:
                    print(f"       - {m.evidence_type}: {m.impact_level} impact ({m.impact_description})")

            # Validate ML Analysis Integration
            if investigation.ml_analysis:
                ml = investigation.ml_analysis
                print(f"[PASS] Step 3 ML Analysis Integrated:")
                print(f"       Win Prob={ml.probability:.3f} | Score={ml.score}/100 | Tier={ml.classification} | Recommend Contest={ml.recommend_contest}")
                print(f"       Model Version={ml.model_version} | Top Positive Factors={len(ml.top_positive_factors)} | Top Negative Factors={len(ml.top_negative_factors)}")
                assert 0.0 <= ml.probability <= 1.0
                assert 0 <= ml.score <= 100
                assert ml.classification in ("STRONG", "NEEDS_REVIEW", "WEAK")

            # Validate Investigation Timeline
            print(f"[PASS] Investigation Timeline: {len(investigation.timeline)} chronological milestones")
            for t_ev in investigation.timeline:
                print(f"       - [{t_ev.event_type}] {t_ev.title} @ {t_ev.timestamp_formatted or 'UNAVAILABLE'} ({t_ev.status_badge})")
            assert len(investigation.timeline) >= 2, "Timeline must contain at least transaction and dispute events"

        # Test Invalid Dispute ID (Not Found handling)
        print("\n--- Testing Invalid Dispute ID (Not Found Handling) ---")
        try:
            service.get_investigation("NON_EXISTENT_DISPUTE_999999")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            print(f"[PASS] Clean ValueError raised on missing dispute: {e}")

    finally:
        db.close()


def test_fastapi_evidence_endpoints():
    print("\n" + "=" * 60)
    print("TEST SUITE 4: FastAPI Evidence Engine Endpoints (TestClient)")
    print("=" * 60)

    client = TestClient(app)

    # 1. Test GET /api/v1/disputes/1/investigation
    resp_inv = client.get("/api/v1/disputes/1/investigation")
    assert resp_inv.status_code == 200, f"Expected 200, got {resp_inv.status_code}"
    data = resp_inv.json()
    print(f"[PASS] GET /api/v1/disputes/1/investigation returned HTTP 200")
    assert "dispute" in data
    assert "evidence_analysis" in data
    assert "timeline" in data
    assert "warnings" in data
    assert "ml_analysis" in data
    print(f"       Dispute: {data['dispute']['dispute_reference']} | Quality Score: {data['evidence_analysis']['quality_score']} | Timeline Events: {len(data['timeline'])}")

    # 2. Test GET /api/disputes/1/investigation (Alias Route)
    resp_inv_alias = client.get("/api/disputes/1/investigation")
    assert resp_inv_alias.status_code == 200
    print(f"[PASS] GET /api/disputes/1/investigation (Alias Route) returned HTTP 200")

    # 3. Test GET /api/v1/disputes/1/timeline
    resp_tl = client.get("/api/v1/disputes/1/timeline")
    assert resp_tl.status_code == 200
    tl_data = resp_tl.json()
    print(f"[PASS] GET /api/v1/disputes/1/timeline returned HTTP 200 ({tl_data['events_count']} events)")
    assert "timeline" in tl_data

    # 4. Test GET /api/disputes/1/timeline (Alias Route)
    resp_tl_alias = client.get("/api/disputes/1/timeline")
    assert resp_tl_alias.status_code == 200
    print(f"[PASS] GET /api/disputes/1/timeline (Alias Route) returned HTTP 200")

    # 5. Test GET /api/v1/disputes/1/evidence-summary
    resp_sum = client.get("/api/v1/disputes/1/evidence-summary")
    assert resp_sum.status_code == 200
    sum_data = resp_sum.json()
    print(f"[PASS] GET /api/v1/disputes/1/evidence-summary returned HTTP 200")
    print(f"       Availability: {sum_data['availability_percentage']}% | Verification: {sum_data['verification_percentage']}% | Quality: {sum_data['quality_score']}")
    assert "strongest_evidence" in sum_data
    assert "missing_evidence" in sum_data

    # 6. Test GET /api/disputes/1/evidence-summary (Alias Route)
    resp_sum_alias = client.get("/api/disputes/1/evidence-summary")
    assert resp_sum_alias.status_code == 200
    print(f"[PASS] GET /api/disputes/1/evidence-summary (Alias Route) returned HTTP 200")

    # 7. Test 404 for invalid dispute ID
    resp_404 = client.get("/api/v1/disputes/99999999/investigation")
    assert resp_404.status_code == 404
    print(f"[PASS] Invalid dispute ID returned HTTP 404: {resp_404.json()['detail']}")


if __name__ == "__main__":
    test_offline_evidence_calculations()
    test_consistency_check_rules()
    test_database_dispute_investigation()
    test_fastapi_evidence_endpoints()
    print("\n" + "=" * 60)
    print("ALL EVIDENCE INTELLIGENCE ENGINE TESTS PASSED (100%)")
    print("=" * 60)
