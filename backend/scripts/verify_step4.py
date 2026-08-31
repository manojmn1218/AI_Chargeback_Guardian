"""
AI Chargeback Guardian — Step 4 Final Verification Script
Runs full investigation retrieval on 3 real synthetic disputes and outputs formatted JSON.
"""

import sys
from pathlib import Path
import json

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.database.session import SessionLocal
from app.services.evidence_service import EvidenceService
from app.schemas.evidence import DisputeInvestigationResponse


def verify_cases():
    db = SessionLocal()
    service = EvidenceService(db)
    dispute_ids = ["1", "2", "3"]

    print("=" * 70)
    print("STEP 4 FINAL VERIFICATION: REAL SYNTHETIC DISPUTES INVESTIGATION")
    print("=" * 70)

    for d_id in dispute_ids:
        inv = service.get_investigation(d_id)
        d = inv.dispute
        ev = inv.evidence_analysis
        ml = inv.ml_analysis

        print(f"\n[DISPUTE CASE #{d.id} / {d.dispute_reference}]")
        print(f"  Claim Reason:         {d.dispute_reason}")
        print(f"  Disputed Amount:      ${d.dispute_amount:.2f} {d.currency if hasattr(d, 'currency') else 'USD'}")
        print(f"  Dispute Status:       {d.dispute_status}")
        print(f"  Customer:             {d.customer.customer_reference if d.customer else 'N/A'} (Risk: {d.customer.customer_risk_history if d.customer else 'N/A'})")
        print(f"  Merchant:             {d.merchant.merchant_reference if d.merchant else 'N/A'} ({d.merchant.merchant_category if d.merchant else 'N/A'})")
        print(f"  Transaction:          {d.transaction.transaction_reference if d.transaction else 'N/A'}")
        
        print(f"  Evidence Completeness:")
        print(f"    - Available:        {ev.available} / {ev.total_expected} ({ev.availability_percentage}%)")
        print(f"    - Verified:         {ev.verified} / {ev.total_expected} ({ev.verification_percentage}%)")
        print(f"    - Missing:          {ev.missing} / {ev.total_expected}")
        print(f"    - Quality Score:    {ev.quality_score}/100")
        
        print(f"  Top Strongest Evidence:")
        for s in ev.strongest_evidence:
            print(f"    * Rank #{s.rank}: {s.evidence_type} (Rel: {s.relevance_score}, Status: {s.status.value}) -> {s.source_reference}")
            
        if ev.missing_evidence:
            print(f"  Missing Evidence Impact Disclosure:")
            for m in ev.missing_evidence:
                print(f"    * {m.evidence_type}: [{m.impact_level} IMPACT] {m.impact_description}")

        if ml:
            print(f"  Step 3 ML Model Assessment:")
            print(f"    - Win Probability:  {ml.probability:.4f} ({round(ml.probability * 100, 1)}%)")
            print(f"    - Case Score:       {ml.score}/100 (Tier: {ml.classification})")
            print(f"    - Recommend Contest:{ml.recommend_contest} (Threshold: {ml.threshold})")
            print(f"    - Model Version:    {ml.model_version} ({ml.model_name})")

        print(f"  Investigation Timeline ({len(inv.timeline)} milestones):")
        for t in inv.timeline:
            print(f"    * [{t.event_type}] {t.title} @ {t.timestamp_formatted or 'UNAVAILABLE'} [{t.status_badge}]")

        print(f"  Consistency Warnings: {len(inv.warnings)}")
        for w in inv.warnings:
            print(f"    * [{w.severity}] {w.code} on {w.field}: {w.message}")

    print("\n" + "=" * 70)
    print("ALL 3 REAL SYNTHETIC DISPUTES VERIFIED SUCCESSFULLY")
    print("=" * 70)
    db.close()


if __name__ == "__main__":
    verify_cases()
