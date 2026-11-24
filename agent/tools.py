
import httpx
import json

ACTING_USER = None

API_HEADERS = {}

def set_acting_user(user):
    global ACTING_USER, API_HEADERS
    ACTING_USER = user
    API_HEADERS = {"X-Acting-User": user}


def get_documents():
    response = httpx.get(
        "http://127.0.0.1:8001/documents",
        headers=API_HEADERS,
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def get_employees():
    response = httpx.get(
        "http://127.0.0.1:8002/employees",
        headers=API_HEADERS,
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def get_financial_reports():
    response = httpx.get(
        "http://127.0.0.1:8003/reports",
        headers=API_HEADERS,
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def get_customers():
    response = httpx.get(
        "http://127.0.0.1:8003/customers",
        headers=API_HEADERS,
        timeout=10
    )
    response.raise_for_status()
    return response.json()


AVAILABLE_FUNCTIONS = {
    "get_documents": get_documents,
    "get_employees": get_employees,
    "get_financial_reports": get_financial_reports,
    "get_customers": get_customers
}


def execute_tool(name, arguments):
    function = AVAILABLE_FUNCTIONS.get(name)

    if function is None:
        return {"error": "Unknown tool"}

    try:
        return function(**arguments)
    except Exception as error:
        return {"error": str(error)}
