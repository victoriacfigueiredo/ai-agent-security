import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

from agent import tools


KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080").rstrip("/")
REALM = os.getenv("KEYCLOAK_REALM", "ai-agent-lab")
CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")

TOKEN_URL = (
    f"{KEYCLOAK_URL}/realms/{REALM}"
    "/protocol/openid-connect/token"
)

BASE_URL = "http://127.0.0.1"

ENDPOINTS = {
    "Documents": (f"{BASE_URL}:8001/documents", 3),
    "Employees": (f"{BASE_URL}:8002/employees", 3),
    "Financial reports": (f"{BASE_URL}:8003/reports", 3),
    "Customers": (f"{BASE_URL}:8003/customers", 2),
}

results = []


def record(name, passed, details=""):
    status = "PASS" if passed else "FAIL"
    results.append({
        "test": name,
        "status": status,
        "details": details,
    })
    print(f"[{status}] {name}")
    if details:
        print(f"       {details}")


def get_token():
    response = httpx.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=10,
        trust_env=False,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERROR: Keycloak client credentials are not configured.")
        sys.exit(1)

    print("\n=== STAGE 2: OAuth2 SECURITY TESTS ===\n")

    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    print("Access token successfully obtained.\n")

    # 1. Valid token: all four resources
    for name, (url, expected_count) in ENDPOINTS.items():
        response = httpx.get(
            url,
            headers=headers,
            timeout=15,
            trust_env=False,
        )

        try:
            data = response.json()
        except ValueError:
            data = None

        passed = (
            response.status_code == 200
            and isinstance(data, list)
            and len(data) == expected_count
        )

        record(
            f"Valid token - {name}",
            passed,
            f"HTTP {response.status_code}; "
            f"records returned: {len(data) if isinstance(data, list) else 'N/A'}",
        )

    # 2. Missing token
    for name, (url, _) in ENDPOINTS.items():
        response = httpx.get(
            url,
            timeout=15,
            trust_env=False,
        )

        record(
            f"Missing token - {name}",
            response.status_code == 401,
            f"HTTP {response.status_code}",
        )

    # 3. Invalid token
    response = httpx.get(
        ENDPOINTS["Customers"][0],
        headers={"Authorization": "Bearer invalid.token.value"},
        timeout=15,
        trust_env=False,
    )

    record(
        "Invalid token rejected",
        response.status_code == 401,
        f"HTTP {response.status_code}",
    )

    # 4. Forged identity header without an access token
    response = httpx.get(
        ENDPOINTS["Customers"][0],
        headers={"X-Acting-User": "Victoria"},
        timeout=15,
        trust_env=False,
    )

    record(
        "Forged X-Acting-User rejected",
        response.status_code == 401,
        f"HTTP {response.status_code}",
    )

    # 5. Bearer token replay from an independent client
    with httpx.Client(
        timeout=15,
        trust_env=False,
    ) as attacker_client:
        response = attacker_client.get(
            ENDPOINTS["Customers"][0],
            headers={"Authorization": f"Bearer {token}"},
        )

    record(
        "Stolen bearer token replay",
        response.status_code == 200,
        f"HTTP {response.status_code}; "
        "a separate client reused the same bearer token",
    )

    # 6. Agent tool integration
    agent_checks = [
        ("Agent - Documents", tools.get_documents, 3),
        ("Agent - Employees", tools.get_employees, 3),
        ("Agent - Financial reports", tools.get_financial_reports, 3),
        ("Agent - Customers", tools.get_customers, 2),
    ]

    for name, function, expected_count in agent_checks:
        try:
            data = function()
            passed = isinstance(data, list) and len(data) == expected_count
            details = f"Records returned: {len(data) if isinstance(data, list) else 'N/A'}"
        except Exception as exc:
            passed = False
            details = f"{type(exc).__name__}: {exc}"

        record(name, passed, details)

    # Save results without storing tokens or secrets
    report = {
        "stage": 2,
        "experiment": "OAuth2 Client Credentials with broad Bearer token",
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "total_tests": len(results),
        "passed": sum(r["status"] == "PASS" for r in results),
        "failed": sum(r["status"] == "FAIL" for r in results),
        "results": results,
    }

    report_dir = Path("research/reports")
    report_dir.mkdir(parents=True, exist_ok=True)

    report_path = report_dir / "stage2-results.json"
    report_path.write_text(json.dumps(report, indent=2))

    print("\n=== SUMMARY ===")
    print(f"Total:  {report['total_tests']}")
    print(f"Passed: {report['passed']}")
    print(f"Failed: {report['failed']}")
    print(f"\nReport saved to: {report_path}")

    if report["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
