"""
AI Chargeback Guardian — Synthetic Data Generator
Generates realistic, fully synthetic chargeback investigation datasets.
Strictly NO real customer information, payment credentials, or financial data.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


def generate_synthetic_data(
    n_customers: int = 750,
    n_merchants: int = 30,
    n_transactions: int = 6000,
    n_disputes: int = 1000,
    random_seed: int = 42,
) -> Dict[str, pd.DataFrame]:
    """
    Generate a full relational synthetic chargeback dataset.

    Returns dictionary containing DataFrames for:
    - customers
    - merchants
    - transactions
    - orders
    - deliveries
    - refunds
    - disputes
    - evidence
    - communications
    - merchant_policies
    - audit_logs
    """
    np.random.seed(random_seed)
    base_date = datetime(2026, 1, 1, 0, 0, 0)

    # 1. GENERATE CUSTOMERS
    customer_ids = [f"CUST-{i+1:06d}" for i in range(n_customers)]
    account_ages = np.random.randint(15, 1200, size=n_customers)
    
    # Previous transactions correlated with account age
    prev_txns = np.maximum(1, (account_ages / 30 * np.random.uniform(0.5, 3.0, size=n_customers)).astype(int))
    
    # Customer risk profiles (80% low, 15% medium, 5% high)
    risk_profiles = np.random.choice(["LOW", "MEDIUM", "HIGH"], size=n_customers, p=[0.80, 0.15, 0.05])
    
    prev_disputes = []
    prev_refunds = []
    for i, r in enumerate(risk_profiles):
        if r == "HIGH":
            disputes_count = int(np.random.poisson(lam=3.5))
            refunds_count = int(np.random.poisson(lam=4.0))
        elif r == "MEDIUM":
            disputes_count = int(np.random.poisson(lam=1.0))
            refunds_count = int(np.random.poisson(lam=1.8))
        else:
            disputes_count = 1 if np.random.rand() < 0.08 else 0
            refunds_count = int(np.random.poisson(lam=0.4))
        prev_disputes.append(disputes_count)
        prev_refunds.append(refunds_count)

    customers_df = pd.DataFrame({
        "id": list(range(1, n_customers + 1)),
        "customer_reference": customer_ids,
        "account_age_days": account_ages,
        "previous_successful_transactions": prev_txns,
        "previous_disputes": prev_disputes,
        "previous_refunds": prev_refunds,
        "customer_risk_history": risk_profiles,
        "created_at": [base_date - timedelta(days=int(age)) for age in account_ages],
    })

    # 2. GENERATE MERCHANTS
    merchant_ids = [f"MER-{i+1:06d}" for i in range(n_merchants)]
    categories = [
        "RETAIL_APPAREL", "ELECTRONICS_HARDWARE", "DIGITAL_SOFTWARE",
        "ONLINE_SUBSCRIPTION", "TRAVEL_HOSPITALITY", "FOOD_DELIVERY", "LUXURY_GOODS"
    ]
    merchant_categories = np.random.choice(categories, size=n_merchants)
    merchant_ages = np.random.randint(90, 2500, size=n_merchants)
    
    # Historical dispute rates by category
    category_dispute_rates = {
        "RETAIL_APPAREL": 0.008, "ELECTRONICS_HARDWARE": 0.018,
        "DIGITAL_SOFTWARE": 0.024, "ONLINE_SUBSCRIPTION": 0.015,
        "TRAVEL_HOSPITALITY": 0.022, "FOOD_DELIVERY": 0.006, "LUXURY_GOODS": 0.030
    }
    hist_disp_rates = [category_dispute_rates[cat] * np.random.uniform(0.6, 1.4) for cat in merchant_categories]
    hist_succ_rates = [1.0 - (disp * np.random.uniform(1.2, 2.5)) for disp in hist_disp_rates]

    merchants_df = pd.DataFrame({
        "id": list(range(1, n_merchants + 1)),
        "merchant_reference": merchant_ids,
        "merchant_category": merchant_categories,
        "account_age_days": merchant_ages,
        "historical_dispute_rate": np.round(hist_disp_rates, 4),
        "historical_success_rate": np.round(hist_succ_rates, 4),
        "created_at": [base_date - timedelta(days=int(age)) for age in merchant_ages],
    })

    # 3. GENERATE TRANSACTIONS, ORDERS & DELIVERIES
    txn_ids = [f"TXN-{i+1:06d}" for i in range(n_transactions)]
    ord_ids = [f"ORD-{i+1:06d}" for i in range(n_transactions)]
    
    assigned_cust_ids = np.random.randint(1, n_customers + 1, size=n_transactions)
    assigned_merch_ids = np.random.randint(1, n_merchants + 1, size=n_transactions)
    
    # Realistic amounts (lognormal distribution with tail)
    base_amounts = np.exp(np.random.normal(loc=4.1, scale=0.9, size=n_transactions))
    amounts = np.round(np.clip(base_amounts, 5.0, 3500.0), 2)
    
    # Timestamps spread over the last 180 days
    txn_offsets_hours = np.random.randint(1, 180 * 24, size=n_transactions)
    txn_timestamps = [base_date + timedelta(hours=int(h)) for h in txn_offsets_hours]
    
    payment_methods = ["CREDIT_CARD", "DEBIT_CARD", "DIGITAL_WALLET", "BANK_TRANSFER"]
    regions = ["US_EAST", "US_WEST", "US_CENTRAL", "EU_WEST", "APAC_SOUTH", "LATAM"]
    
    payment_types = np.random.choice(payment_methods, size=n_transactions, p=[0.55, 0.25, 0.15, 0.05])
    device_refs = [f"DEV-{np.random.randint(1000, 999999):06d}" for _ in range(n_transactions)]
    location_regions = np.random.choice(regions, size=n_transactions)
    frequencies = np.round(np.random.exponential(scale=1.5, size=n_transactions) + 0.5, 2)
    deviations = np.round(np.random.normal(loc=0.0, scale=0.8, size=n_transactions), 2)

    transactions_df = pd.DataFrame({
        "id": list(range(1, n_transactions + 1)),
        "transaction_reference": txn_ids,
        "customer_id": assigned_cust_ids,
        "merchant_id": assigned_merch_ids,
        "amount": amounts,
        "currency": ["USD"] * n_transactions,
        "transaction_timestamp": txn_timestamps,
        "transaction_status": ["SUCCESS"] * n_transactions,
        "payment_method_type": payment_types,
        "device_reference": device_refs,
        "location_region": location_regions,
        "transaction_frequency": frequencies,
        "amount_deviation": deviations,
        "created_at": txn_timestamps,
    })

    # Orders linked 1:1 to transactions
    orders_df = pd.DataFrame({
        "id": list(range(1, n_transactions + 1)),
        "order_reference": ord_ids,
        "transaction_id": list(range(1, n_transactions + 1)),
        "order_value": amounts,
        "product_category": [merchant_categories[m_idx] for m_idx in (assigned_merch_ids - 1)],
        "order_timestamp": txn_timestamps,
        "fulfillment_status": ["FULFILLED"] * n_transactions,
        "created_at": txn_timestamps,
    })

    # Deliveries linked to orders
    delivery_status_choices = ["DELIVERED", "IN_TRANSIT", "RETURNED"]
    deliv_statuses = np.random.choice(delivery_status_choices, size=n_transactions, p=[0.92, 0.06, 0.02])
    tracking_avails = [True if s != "RETURNED" else np.random.rand() > 0.3 for s in deliv_statuses]
    deliv_confirmed = [True if s == "DELIVERED" and np.random.rand() > 0.08 else False for s in deliv_statuses]
    cust_acknowledged = [True if conf and np.random.rand() > 0.35 else False for conf in deliv_confirmed]

    shipped_times = [t + timedelta(hours=int(np.random.randint(6, 48))) for t in txn_timestamps]
    delivered_times = [
        s + timedelta(days=int(np.random.randint(2, 6))) if conf else None
        for s, conf in zip(shipped_times, deliv_confirmed)
    ]

    deliveries_df = pd.DataFrame({
        "id": list(range(1, n_transactions + 1)),
        "order_id": list(range(1, n_transactions + 1)),
        "delivery_status": deliv_statuses,
        "shipped_at": shipped_times,
        "delivered_at": delivered_times,
        "tracking_available": tracking_avails,
        "delivery_confirmed": deliv_confirmed,
        "customer_acknowledged": cust_acknowledged,
        "created_at": shipped_times,
    })

    # 4. GENERATE REFUNDS (~10% of transactions)
    n_refunds = int(n_transactions * 0.10)
    refunded_txn_indices = np.random.choice(range(1, n_transactions + 1), size=n_refunds, replace=False)
    refund_reasons = [
        "CUSTOMER_SATISFACTION", "DAMAGED_IN_TRANSIT", "ORDER_CANCELLATION",
        "DEFECTIVE_PRODUCT", "WRONG_SIZE_RETURN", "DUPLICATE_PURCHASE"
    ]
    refund_amounts = [transactions_df.loc[idx - 1, "amount"] for idx in refunded_txn_indices]
    refund_timestamps = [
        transactions_df.loc[idx - 1, "transaction_timestamp"] + timedelta(days=int(np.random.randint(1, 14)))
        for idx in refunded_txn_indices
    ]

    refunds_df = pd.DataFrame({
        "id": list(range(1, n_refunds + 1)),
        "transaction_id": refunded_txn_indices,
        "refund_status": ["PROCESSED"] * n_refunds,
        "refund_amount": refund_amounts,
        "refund_timestamp": refund_timestamps,
        "refund_reason": np.random.choice(refund_reasons, size=n_refunds),
        "created_at": refund_timestamps,
    })

    # 5. GENERATE DISPUTES
    # Sample transactions to be disputed
    disputed_txn_indices = np.random.choice(range(1, n_transactions + 1), size=n_disputes, replace=False)
    dispute_ids = [f"DISP-{i+1:06d}" for i in range(n_disputes)]

    dispute_reasons_pool = [
        "GOODS_NOT_RECEIVED",
        "UNAUTHORIZED_TRANSACTION",
        "GOODS_NOT_AS_DESCRIBED",
        "DUPLICATE_TRANSACTION",
        "REFUND_NOT_RECEIVED"
    ]
    dispute_reasons = np.random.choice(dispute_reasons_pool, size=n_disputes, p=[0.38, 0.30, 0.16, 0.08, 0.08])

    dispute_cust_ids = [transactions_df.loc[idx - 1, "customer_id"] for idx in disputed_txn_indices]
    dispute_merch_ids = [transactions_df.loc[idx - 1, "merchant_id"] for idx in disputed_txn_indices]
    dispute_amounts = [transactions_df.loc[idx - 1, "amount"] for idx in disputed_txn_indices]
    dispute_timestamps = [
        transactions_df.loc[idx - 1, "transaction_timestamp"] + timedelta(days=int(np.random.randint(5, 45)))
        for idx in disputed_txn_indices
    ]

    # Calculate ground truth outcome (1 = Merchant Win/Contest Success, 0 = Merchant Lost/Fraud)
    # Realistic ground truth formula with correlation & noise
    outcomes = []
    for i, idx in enumerate(disputed_txn_indices):
        c_id = dispute_cust_ids[i]
        deliv = deliveries_df.loc[idx - 1]
        cust = customers_df.loc[c_id - 1]
        amt = dispute_amounts[i]
        reason = dispute_reasons[i]

        # Base win probability (tuned for realistic 65-70% contest success rate)
        win_score = 0.40

        # Positive indicators for merchant
        if deliv["delivery_confirmed"]:
            win_score += 0.22
        if deliv["customer_acknowledged"]:
            win_score += 0.14
        if deliv["tracking_available"]:
            win_score += 0.06
        if cust["previous_successful_transactions"] > 5:
            win_score += 0.08
        if cust["customer_risk_history"] == "LOW":
            win_score += 0.06

        # Negative indicators for merchant / Risk indicators
        if reason == "UNAUTHORIZED_TRANSACTION":
            win_score -= 0.22
        if reason == "GOODS_NOT_RECEIVED" and not deliv["delivery_confirmed"]:
            win_score -= 0.38
        if reason == "REFUND_NOT_RECEIVED":
            win_score -= 0.25
        if cust["previous_disputes"] > 1:
            win_score -= 0.16
        if amt > 400:
            win_score -= 0.12
        if cust["customer_risk_history"] == "HIGH":
            win_score -= 0.20

        # Add stochastic real-world noise
        win_score += np.random.normal(loc=0.0, scale=0.15)
        win_prob = np.clip(win_score, 0.05, 0.95)

        outcome = 1 if np.random.rand() < win_prob else 0
        outcomes.append(outcome)

    dispute_statuses = np.random.choice(["RESOLVED", "UNDER_REVIEW", "OPEN", "CLOSED"], size=n_disputes, p=[0.70, 0.15, 0.10, 0.05])

    disputes_df = pd.DataFrame({
        "id": list(range(1, n_disputes + 1)),
        "dispute_reference": dispute_ids,
        "transaction_id": disputed_txn_indices,
        "customer_id": dispute_cust_ids,
        "merchant_id": dispute_merch_ids,
        "dispute_reason": dispute_reasons,
        "dispute_amount": dispute_amounts,
        "dispute_status": dispute_statuses,
        "dispute_timestamp": dispute_timestamps,
        "outcome": outcomes,
        "created_at": dispute_timestamps,
    })

    # 6. GENERATE EVIDENCE (7 categories per dispute)
    evidence_types = [
        "PAYMENT", "INVOICE", "ORDER", "DELIVERY",
        "REFUND", "CUSTOMER_COMMUNICATION", "MERCHANT_POLICY"
    ]
    evidence_rows = []
    ev_id_counter = 1

    for i, d_row in disputes_df.iterrows():
        d_id = d_row["id"]
        txn_idx = d_row["transaction_id"]
        deliv = deliveries_df.loc[txn_idx - 1]
        outcome = d_row["outcome"]
        d_time = d_row["dispute_timestamp"]

        for ev_type in evidence_types:
            # Availability logic correlated with outcome and delivery status
            if ev_type == "PAYMENT":
                avail = True
                desc = "3D Secure 2.0 gateway transaction authorization log"
                src = "PAYMENT_GATEWAY_AUTH"
            elif ev_type == "INVOICE":
                avail = True if np.random.rand() > 0.04 else False
                desc = "Itemized digital invoice with billing address match"
                src = "ERP_BILLING_SYSTEM"
            elif ev_type == "ORDER":
                avail = True if np.random.rand() > 0.03 else False
                desc = "Order confirmation record and checkout timestamp"
                src = "COMMERCE_ORDER_DB"
            elif ev_type == "DELIVERY":
                avail = bool(deliv["delivery_confirmed"])
                desc = "Signed carrier proof of delivery with GPS tracking coordinates" if avail else "Carrier delivery tracking incomplete or missing signature"
                src = "CARRIER_API_FEDEX"
            elif ev_type == "REFUND":
                has_refund = txn_idx in refunded_txn_indices
                avail = has_refund
                desc = "Refund audit record" if avail else "No prior refund request on file"
                src = "REFUND_SERVICE_LOG"
            elif ev_type == "CUSTOMER_COMMUNICATION":
                avail = True if (deliv["customer_acknowledged"] or np.random.rand() > 0.40) else False
                desc = "Customer support ticket and chat transcript" if avail else "No pre-dispute support correspondence found"
                src = "SUPPORT_CRM_ZENDESK"
            elif ev_type == "MERCHANT_POLICY":
                avail = True if np.random.rand() > 0.05 else False
                desc = "Accepted Terms of Service and Merchant Refund Policy at checkout"
                src = "POLICY_ENGINE"

            verified = bool(avail and (np.random.rand() > 0.08))

            evidence_rows.append({
                "id": ev_id_counter,
                "dispute_id": d_id,
                "evidence_type": ev_type,
                "description": desc,
                "source_reference": src,
                "available": avail,
                "verified": verified,
                "evidence_timestamp": d_time + timedelta(hours=int(np.random.randint(1, 12))),
                "created_at": d_time,
            })
            ev_id_counter += 1

    evidence_df = pd.DataFrame(evidence_rows)

    # 7. GENERATE COMMUNICATIONS & AUDIT LOGS
    comm_rows = []
    audit_rows = []
    comm_id_counter = 1
    audit_id_counter = 1

    for i, d_row in disputes_df.iterrows():
        d_id = d_row["id"]
        d_time = d_row["dispute_timestamp"]

        # 1-2 communications per dispute
        n_comms = np.random.choice([0, 1, 2], p=[0.2, 0.6, 0.2])
        for c_idx in range(n_comms):
            c_type = np.random.choice(["SUPPORT_CHAT", "EMAIL", "PHONE_LOG"])
            comm_rows.append({
                "id": comm_id_counter,
                "dispute_id": d_id,
                "communication_type": c_type,
                "communication_timestamp": d_time - timedelta(days=int(np.random.randint(1, 10))),
                "verified": True if np.random.rand() > 0.1 else False,
                "content_summary": f"Customer inquired about order status under ticket #{np.random.randint(1000, 9999)}.",
                "created_at": d_time,
            })
            comm_id_counter += 1

        # Audit logs for dispute lifecycle
        audit_rows.append({
            "id": audit_id_counter,
            "dispute_id": d_id,
            "action": "DISPUTE_INGESTED",
            "actor_type": "SYSTEM",
            "metadata_json": '{"channel": "PAYMENT_NETWORK_WEBHOOK"}',
            "timestamp": d_time,
        })
        audit_id_counter += 1

        audit_rows.append({
            "id": audit_id_counter,
            "dispute_id": d_id,
            "action": "EVIDENCE_RETRIEVAL_COMPLETED",
            "actor_type": "SYSTEM",
            "metadata_json": '{"evidence_count": 7}',
            "timestamp": d_time + timedelta(seconds=15),
        })
        audit_id_counter += 1

    communications_df = pd.DataFrame(comm_rows)
    audit_logs_df = pd.DataFrame(audit_rows)

    # 8. MERCHANT POLICIES
    policy_rows = []
    p_id_counter = 1
    for m_id in range(1, n_merchants + 1):
        for p_type in ["TERMS_OF_SERVICE", "REFUND_POLICY", "SHIPPING_POLICY"]:
            policy_rows.append({
                "id": p_id_counter,
                "merchant_id": m_id,
                "policy_type": p_type,
                "policy_text": f"Standard merchant {p_type.lower().replace('_', ' ')}: All claims must be filed within 30 days of confirmed delivery.",
                "active": True,
                "created_at": base_date - timedelta(days=365),
            })
            p_id_counter += 1

    merchant_policies_df = pd.DataFrame(policy_rows)

    return {
        "customers": customers_df,
        "merchants": merchants_df,
        "transactions": transactions_df,
        "orders": orders_df,
        "deliveries": deliveries_df,
        "refunds": refunds_df,
        "disputes": disputes_df,
        "evidence": evidence_df,
        "communications": communications_df,
        "merchant_policies": merchant_policies_df,
        "audit_logs": audit_logs_df,
    }


def export_ml_dataset(
    data: Dict[str, pd.DataFrame],
    output_path: Path | None = None,
) -> pd.DataFrame:
    """
    Construct a clean ML-ready tabular dataset from relational synthetic tables.
    Contains no PII, no IDs that cause target leakage, and 16 clean numerical/categorical features.
    """
    disputes = data["disputes"]
    transactions = data["transactions"]
    customers = data["customers"]
    merchants = data["merchants"]
    deliveries = data["deliveries"]
    evidence = data["evidence"]
    refunds = data["refunds"]
    communications = data["communications"]

    # Pre-aggregate evidence available counts per dispute
    ev_counts = evidence[evidence["available"]].groupby("dispute_id").size().to_dict()
    ev_verified_counts = evidence[evidence["verified"]].groupby("dispute_id").size().to_dict()

    # Pre-aggregate communications per dispute
    comm_counts = communications.groupby("dispute_id").size().to_dict()

    # Pre-index refunds by transaction_id
    refunded_txns = set(refunds["transaction_id"].unique())

    ml_rows = []
    for _, d in disputes.iterrows():
        d_id = int(d["id"])
        txn_id = int(d["transaction_id"])
        cust_id = int(d["customer_id"])
        merch_id = int(d["merchant_id"])

        txn = transactions.loc[txn_id - 1]
        cust = customers.loc[cust_id - 1]
        merch = merchants.loc[merch_id - 1]
        deliv = deliveries.loc[txn_id - 1]

        # Features matching specification
        txn_amount = float(txn["amount"])
        txn_age = max(1, (d["dispute_timestamp"] - txn["transaction_timestamp"]).days)
        cust_account_age = int(cust["account_age_days"])
        prev_disputes = int(cust["previous_disputes"])
        prev_txns = int(cust["previous_successful_transactions"])
        prev_refunds = int(cust["previous_refunds"])
        deliv_confirmed = 1 if bool(deliv["delivery_confirmed"]) else 0
        cust_acknowledged = 1 if bool(deliv["customer_acknowledged"]) else 0
        refund_proc = 1 if txn_id in refunded_txns else 0
        comm_avail = 1 if comm_counts.get(d_id, 0) > 0 else 0
        ev_count = ev_counts.get(d_id, 0)
        merch_disp_rate = round(float(merch["historical_dispute_rate"]), 4)
        txn_freq = float(txn["transaction_frequency"])
        amt_dev = float(txn["amount_deviation"])
        disp_reason = str(d["dispute_reason"])
        pay_method = str(txn["payment_method_type"])

        # Target Variable: 1 = Merchant Win (Contest Success), 0 = Merchant Lost (Chargeback Upheld)
        outcome = int(d["outcome"])

        ml_rows.append({
            "transaction_amount": txn_amount,
            "transaction_age": txn_age,
            "customer_account_age": cust_account_age,
            "previous_disputes": prev_disputes,
            "previous_successful_transactions": prev_txns,
            "previous_refunds": prev_refunds,
            "delivery_confirmed": deliv_confirmed,
            "customer_acknowledged": cust_acknowledged,
            "refund_processed": refund_proc,
            "communication_available": comm_avail,
            "evidence_count": ev_count,
            "merchant_dispute_rate": merch_disp_rate,
            "transaction_frequency": txn_freq,
            "amount_deviation": amt_dev,
            "dispute_reason": disp_reason,
            "payment_method": pay_method,
            "outcome": outcome,
        })

    ml_df = pd.DataFrame(ml_rows)

    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        ml_df.to_csv(out_p, index=False)

    return ml_df


def load_dataset(path: Path) -> pd.DataFrame:
    """Load the synthetic ML dataset from CSV."""
    return pd.read_csv(path)

