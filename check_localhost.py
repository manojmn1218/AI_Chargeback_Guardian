"""
AI Chargeback Guardian — Localhost Connectivity & Health Inspector

Checks:
1. Backend Root Health (http://127.0.0.1:8000/health)
2. OpenAPI / Swagger Docs (http://127.0.0.1:8000/docs)
3. Relational Disputes API (http://127.0.0.1:8000/api/v1/disputes)
4. Investigation & Evidence API (http://127.0.0.1:8000/api/v1/disputes/1/investigation)
5. Analytics Overview API (http://127.0.0.1:8000/api/v1/analytics/overview)
6. Unified Single-Port Application (http://127.0.0.1:8000/)
7. Vite Dev Hot-Reload Server (http://127.0.0.1:5173/)
"""

import urllib.request
import json
import sys


def check():
    print("=" * 70)
    print("AI CHARGEBACK GUARDIAN — LOCALHOST CONNECTIVITY INSPECTION")
    print("=" * 70)

    # 1. Backend Root Health
    print("\n[1/6] Backend Health (http://127.0.0.1:8000/health)...")
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=3) as resp:
            data = json.loads(resp.read().decode())
            print(f"  [OK] Status: {data.get('status')} | Version: {data.get('version')}")
    except Exception as e:
        print(f"  [FAIL] Backend server not reachable: {e}")

    # 2. OpenAPI / Swagger Docs
    print("\n[2/6] Swagger Docs (http://127.0.0.1:8000/docs)...")
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/docs", timeout=3) as resp:
            print(f"  [OK] HTTP {resp.status} — Interactive API Docs Accessible")
    except Exception as e:
        print(f"  [FAIL] Swagger docs unreachable: {e}")

    # 3. Relational Disputes API
    print("\n[3/6] Disputes API (http://127.0.0.1:8000/api/v1/disputes)...")
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/disputes?page=1&page_size=5", timeout=3) as resp:
            data = json.loads(resp.read().decode())
            print(f"  [OK] HTTP {resp.status} — Total Disputes in DB: {data.get('total')}")
    except Exception as e:
        print(f"  [FAIL] Disputes API unreachable: {e}")

    # 4. Investigation API
    print("\n[4/6] Investigation API (http://127.0.0.1:8000/api/v1/disputes/1/investigation)...")
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/disputes/1/investigation", timeout=3) as resp:
            data = json.loads(resp.read().decode())
            ev = data.get("evidence_analysis", {})
            print(f"  [OK] Dispute: {data['dispute']['dispute_reference']} | Quality Score: {ev.get('quality_score')}/100 | Evidence: {ev.get('available')}/{ev.get('total_expected')}")
    except Exception as e:
        print(f"  [FAIL] Investigation API unreachable: {e}")

    # 5. Analytics Overview API
    print("\n[5/6] Analytics Overview (http://127.0.0.1:8000/api/v1/analytics/overview)...")
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/analytics/overview", timeout=3) as resp:
            data = json.loads(resp.read().decode())
            print(f"  [OK] HTTP {resp.status} — Total: {data.get('total_disputes')} | Avg Strength: {data.get('average_case_strength')}%")
    except Exception as e:
        print(f"  [FAIL] Analytics API unreachable: {e}")

    # 6. Unified Frontend Application
    print("\n[6/6] Unified Application (http://127.0.0.1:8000/)...")
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/", timeout=3) as resp:
            html = resp.read().decode()
            has_root = "root" in html
            print(f"  [OK] HTTP {resp.status} — React SPA Container: {'Verified' if has_root else 'Missing root'}")
    except Exception as e:
        print(f"  [FAIL] Unified Frontend unreachable on port 8000: {e}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    check()
