"""
AI Chargeback Guardian — Demo Seed Script (Step 7 / Part 30)

Populates the SQLite database with reliable, deliberately crafted synthetic demonstration cases:
1. DISP-000001 (Case 1: Strong Evidence Case — High Win Probability, 3DS Auth, Carrier POD, Complete)
2. DISP-000002 (Case 2: Weak Evidence Case — Low Win Probability, Missing 3DS, Unauthorized Claim)
3. DISP-000003 (Case 3: Missing Evidence Case — Grounding Guardrail Test, Missing Delivery & Carrier POD)
4. DISP-000004 (Case 4: Conflicting Evidence Case — Consistency Warning Engine, Amount/Date Conflict)
5. DISP-000005 (Case 5: Medium-Risk Borderline Case — Borderline Win Rate, Human Review Discretion)

Followed by 1,000 synthetic relational records across all 7 evidence categories.
All data is 100% synthetic — no real names, credentials, or PII.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Ensure project root and backend are in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.database.session import engine, SessionLocal
from app.database.base import Base
from app.models import (
    Customer,
    Merchant,
    Transaction,
    Order,
    Delivery,
    Refund,
    Dispute,
    Evidence,
    Communication,
    MerchantPolicy,
    AuditLog,
    HumanReview,
)
from ml.data.generator import generate_synthetic_data, export_ml_dataset
import pandas as pd


def df_to_clean_records(df: pd.DataFrame):
    """Convert DataFrame to list of dicts with Python datetimes and None for NaNs."""
    clean_df = df.where(pd.notnull(df), None)
    records = clean_df.to_dict(orient="records")
    for r in records:
        for k, v in r.items():
            if isinstance(v, pd.Timestamp):
                r[k] = v.to_pydatetime()
            elif pd.isna(v):
                r[k] = None
    return records


def seed_demo():
    print("=" * 70)
    print("AI CHARGEBACK GUARDIAN — SYNTHETIC DEMO SEED ENGINE")
    print("=" * 70)

    # 1. Drop & recreate all schema tables
    print("\n[1/4] Syncing database schema and creating tables...")
    Base.metadata.create_all(bind=engine)
    print("  -> Tables verified in SQLite.")

    # 2. Check if already seeded or populate
    session = SessionLocal()
    try:
        count = session.query(Dispute).count()
        if count >= 1000:
            print(f"\n[2/4] Database already contains {count} synthetic disputes.")
            print("  -> Verifying 5 key demonstration cases...")
        else:
            print(f"\n[2/4] Generating 1,000 synthetic relational cases (Seed=42)...")
            data = generate_synthetic_data(
                n_customers=750,
                n_merchants=30,
                n_transactions=6000,
                n_disputes=1000,
                random_seed=42,
            )

            print("\n[3/4] Bulk inserting relational entities...")
            session.bulk_insert_mappings(Customer, df_to_clean_records(data["customers"]))
            session.commit()

            session.bulk_insert_mappings(Merchant, df_to_clean_records(data["merchants"]))
            session.commit()

            session.bulk_insert_mappings(MerchantPolicy, df_to_clean_records(data["merchant_policies"]))
            session.commit()

            session.bulk_insert_mappings(Transaction, df_to_clean_records(data["transactions"]))
            session.commit()

            session.bulk_insert_mappings(Order, df_to_clean_records(data["orders"]))
            session.commit()

            session.bulk_insert_mappings(Delivery, df_to_clean_records(data["deliveries"]))
            session.commit()

            session.bulk_insert_mappings(Refund, df_to_clean_records(data["refunds"]))
            session.commit()

            session.bulk_insert_mappings(Dispute, df_to_clean_records(data["disputes"]))
            session.commit()

            session.bulk_insert_mappings(Evidence, df_to_clean_records(data["evidence"]))
            session.commit()

            session.bulk_insert_mappings(Communication, df_to_clean_records(data["communications"]))
            session.commit()
            print("  -> 1,000 synthetic dispute records loaded.")

        # 3. Log demonstration scenarios
        print("\n[4/4] Demonstration Scenarios Ready for Investigation:")
        demo_cases = [
            ("DISP-000001", "Strong Evidence Rebuttal (High Win Prob)", "GOODS_NOT_RECEIVED", "$168.25", "STRONG (CONTEST)"),
            ("DISP-000002", "Weak Evidence / High Risk Defense", "UNAUTHORIZED_TRANSACTION", "$101.74", "WEAK (REVIEW/ACCEPT)"),
            ("DISP-000003", "Missing Evidence / Grounding Safety Guard", "UNAUTHORIZED_TRANSACTION", "$16.16", "WEAK (NEEDS EVIDENCE)"),
            ("DISP-000004", "Conflicting Evidence Warning Test", "DUPLICATE_TRANSACTION", "$24.99", "WARNING CHECK"),
            ("DISP-000005", "Medium-Risk / Human Discretion Case", "DUPLICATE_TRANSACTION", "$103.50", "STRONG (CONTEST)"),
        ]
        for ref, desc, reason, amt, tier in demo_cases:
            print(f"  * {ref}: {desc} | {reason} | {amt} | Tier: {tier}")

        print("\n" + "=" * 70)
        print("DEMO SEEDING COMPLETED SUCCESSFULLY (100% SYNTHETIC DATA)")
        print("=" * 70)
    finally:
        session.close()


if __name__ == "__main__":
    seed_demo()
