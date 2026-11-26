import os
import time

import httpx


KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080").rstrip("/")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "ai-agent-lab")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")

TOKEN_URL = (
    f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}"
    "/protocol/openid-connect/token"
)

_access_token = None
_token_expires_at = 0


def get_access_token():
    global _access_token, _token_expires_at

    if _access_token and time.monotonic() < _token_expires_at:
        return _access_token

    if not KEYCLOAK_CLIENT_ID or not KEYCLOAK_CLIENT_SECRET:
        raise RuntimeError("Keycloak client credentials are not configured")

    response = httpx.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": KEYCLOAK_CLIENT_ID,
            "client_secret": KEYCLOAK_CLIENT_SECRET,
        },
        timeout=10,
        trust_env=False,
    )
    response.raise_for_status()

    token_data = response.json()
    _access_token = token_data["access_token"]
    _token_expires_at = time.monotonic() + token_data.get("expires_in", 300) - 30

    print("[OAUTH2] Access token obtained from Keycloak")

    return _access_token


def api_headers():
    return {"Authorization": f"Bearer {get_access_token()}"}


def get_documents():
    response = httpx.get(
        "http://127.0.0.1:8001/documents",
        headers=api_headers(),
        timeout=10,
        trust_env=False,
    )
    response.raise_for_status()
    return response.json()


def get_employees():
    response = httpx.get(
        "http://127.0.0.1:8002/employees",
        headers=api_headers(),
        timeout=10,
        trust_env=False,
    )
    response.raise_for_status()
    return response.json()


def get_financial_reports():
    response = httpx.get(
        "http://127.0.0.1:8003/reports",
        headers=api_headers(),
        timeout=10,
        trust_env=False,
    )
    response.raise_for_status()
    return response.json()


def get_customers():
    response = httpx.get(
        "http://127.0.0.1:8003/customers",
        headers=api_headers(),
        timeout=10,
        trust_env=False,
    )
    response.raise_for_status()
    return response.json()



AVAILABLE_FUNCTIONS = {
    "get_documents": get_documents,
    "get_employees": get_employees,
    "get_financial_reports": get_financial_reports,
    "get_customers": get_customers,
}


def execute_tool(name, arguments):
    function = AVAILABLE_FUNCTIONS.get(name)

    if function is None:
        return {"error": "Unknown tool"}

    try:
        return function(**arguments)
    except Exception as error:
        return {"error": str(error)}
