"""
AI Chargeback Guardian — Database Seeding Script (Step 2)
Initializes database tables, generates realistic synthetic data,
seeds SQLite database using high-performance bulk operations,
and exports the ML training dataset.
"""

import sys
from pathlib import Path
import pandas as pd

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
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
)
from ml.data.generator import generate_synthetic_data, export_ml_dataset


def df_to_clean_records(df: pd.DataFrame):
    """Convert a DataFrame to a list of dicts, replacing NaT/NaN with None."""
    clean_df = df.where(pd.notnull(df), None)
    records = clean_df.to_dict(orient="records")
    # Convert any remaining pandas Timestamps to python datetimes
    for r in records:
        for k, v in r.items():
            if isinstance(v, pd.Timestamp):
                r[k] = v.to_pydatetime()
            elif pd.isna(v):
                r[k] = None
    return records


def seed_database():
    """Seed the SQLite database with realistic relational synthetic records."""
    print("=" * 60)
    print("AI Chargeback Guardian — Database Seeding & Synthetic Data")
    print("=" * 60)

    # 1. Reset and create all tables
    print("\n[1/4] Dropping and re-creating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("  -> Tables created successfully.")

    # 2. Generate synthetic data
    print("\n[2/4] Generating synthetic relational records (random_seed=42)...")
    data = generate_synthetic_data(
        n_customers=750,
        n_merchants=30,
        n_transactions=6000,
        n_disputes=1000,
        random_seed=42,
    )
    print("  -> Synthetic dataset generated in memory.")

    # 3. Seed into SQLite using clean dictionaries
    print("\n[3/4] Inserting records into SQLite with foreign key integrity...")
    session = SessionLocal()
    try:
        # Customers
        session.bulk_insert_mappings(Customer, df_to_clean_records(data["customers"]))
        session.commit()

        # Merchants
        session.bulk_insert_mappings(Merchant, df_to_clean_records(data["merchants"]))
        session.commit()

        # Merchant Policies
        session.bulk_insert_mappings(MerchantPolicy, df_to_clean_records(data["merchant_policies"]))
        session.commit()

        # Transactions
        session.bulk_insert_mappings(Transaction, df_to_clean_records(data["transactions"]))
        session.commit()

        # Orders
        session.bulk_insert_mappings(Order, df_to_clean_records(data["orders"]))
        session.commit()

        # Deliveries
        session.bulk_insert_mappings(Delivery, df_to_clean_records(data["deliveries"]))
        session.commit()

        # Refunds
        session.bulk_insert_mappings(Refund, df_to_clean_records(data["refunds"]))
        session.commit()

        # Disputes
        session.bulk_insert_mappings(Dispute, df_to_clean_records(data["disputes"]))
        session.commit()

        # Evidence
        session.bulk_insert_mappings(Evidence, df_to_clean_records(data["evidence"]))
        session.commit()

        # Communications
        session.bulk_insert_mappings(Communication, df_to_clean_records(data["communications"]))
        session.commit()

        # Audit Logs
        session.bulk_insert_mappings(AuditLog, df_to_clean_records(data["audit_logs"]))
        session.commit()

        print("  -> All records successfully committed to SQLite database.")

    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        session.close()

    # 4. Export clean ML CSV
    print("\n[4/4] Exporting ML-ready tabular dataset (chargeback_ml_dataset.csv)...")
    ml_export_path = ROOT_DIR / "data" / "synthetic" / "chargeback_ml_dataset.csv"
    ml_df = export_ml_dataset(data, output_path=ml_export_path)
    print(f"  -> Exported {len(ml_df)} rows with {len(ml_df.columns)} features to: {ml_export_path}")

    # Summary Report
    print("\n" + "=" * 60)
    print("DATABASE SEEDING SUMMARY")
    print("=" * 60)
    print(f"  Customers:            {len(data['customers']):>6,}")
    print(f"  Merchants:            {len(data['merchants']):>6,}")
    print(f"  Merchant Policies:    {len(data['merchant_policies']):>6,}")
    print(f"  Transactions:         {len(data['transactions']):>6,}")
    print(f"  Orders:               {len(data['orders']):>6,}")
    print(f"  Deliveries:           {len(data['deliveries']):>6,}")
    print(f"  Refunds:              {len(data['refunds']):>6,}")
    print(f"  Disputes:             {len(data['disputes']):>6,}")
    print(f"  Evidence Records:     {len(data['evidence']):>6,}")
    print(f"  Communications:       {len(data['communications']):>6,}")
    print(f"  Audit Logs:           {len(data['audit_logs']):>6,}")
    print(f"  ML Dataset Rows:      {len(ml_df):>6,}")
    print("=" * 60)
    print("Synthetic database initialization complete. Zero PII used.")
    print("=" * 60)


if __name__ == "__main__":
    seed_database()
