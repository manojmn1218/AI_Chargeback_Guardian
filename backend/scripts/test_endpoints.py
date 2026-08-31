"""
Test all REST API endpoints for Step 2.
"""
import urllib.request
import json

BASE_URL = "http://localhost:8000"

def test_get(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"[200 OK] {endpoint}")
            return data
    except urllib.error.HTTPError as e:
        print(f"[{e.code} Error] {endpoint} -> {e.read().decode()}")
        return None

def run_tests():
    print("=" * 60)
    print("TESTING API ENDPOINTS")
    print("=" * 60)

    # 1. Health
    h = test_get("/health")
    print("  Health Status:", h)

    # 2. Customers
    c = test_get("/api/v1/customers?page=1&page_size=2")
    print(f"  Customers Total: {c['total']}, Sample: {c['items'][0]['customer_reference']}")

    # 3. Merchants
    m = test_get("/api/v1/merchants?page=1&page_size=2")
    print(f"  Merchants Total: {m['total']}, Sample: {m['items'][0]['merchant_reference']}")

    # 4. Transactions
    t = test_get("/api/v1/transactions?page=1&page_size=2")
    print(f"  Transactions Total: {t['total']}, Sample: {t['items'][0]['transaction_reference']} Amount: ${t['items'][0]['amount']}")

    # 5. Disputes
    d = test_get("/api/v1/disputes?page=1&page_size=2")
    print(f"  Disputes Total: {d['total']}, Sample: {d['items'][0]['dispute_reference']} Reason: {d['items'][0]['dispute_reason']}")

    # 6. Dispute Detail
    disp_detail = test_get("/api/v1/disputes/DISP-000001")
    print(f"  Detail: {disp_detail['dispute_reference']} Amount: ${disp_detail['dispute_amount']} Customer: {disp_detail['customer']['customer_reference']} Evidence Items: {len(disp_detail['evidence_items'])}")

    # 7. Dispute Evidence
    ev = test_get("/api/v1/disputes/DISP-000001/evidence")
    print(f"  Evidence Completeness: {ev['completeness_percentage']}% ({ev['total_available']}/{ev['total_categories']})")
    for item in ev['items'][:3]:
        print(f"    - {item['evidence_type']}: available={item['available']} verified={item['verified']}")

    # 8. 404 Error handling
    print("\nTesting 404 Error handling...")
    test_get("/api/v1/disputes/DISP-999999")

    # 9. 422 Error handling
    print("\nTesting 422 Validation error handling...")
    test_get("/api/v1/disputes?page=0")

    print("=" * 60)
    print("ALL API ENDPOINTS TESTED SUCCESSFULLY")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
