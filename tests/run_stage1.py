
import json
import sys
from datetime import datetime
from pathlib import Path

import httpx


BASE_URLS = {
    "documents": "http://127.0.0.1:8001",
    "hr": "http://127.0.0.1:8002",
    "finance": "http://127.0.0.1:8003",
}

USERS = {
    "Victoria": "Engineering",
    "Felipe": "Human Resources",
    "Jodson": "Finance",
}


def scenario(user, service, path, expected_status,
             field=None, expected_value=None, description=""):
    return {
        "user": user,
        "service": service,
        "path": path,
        "expected_status": expected_status,
        "field": field,
        "expected_value": expected_value,
        "description": description,
    }


SCENARIOS = []

for user, department in USERS.items():
    SCENARIOS.extend([
        scenario(
            user, "documents", "/documents", 200,
            "ids",
            [1] + (
                [2] if user == "Felipe" else
                [3] if user == "Jodson" else []
            ),
            "List documents permitted to the user"
        ),
        scenario(
            user, "hr", "/employees", 200,
            "names", [user],
            "List employee profiles permitted to the user"
        ),
        scenario(
            user, "finance", "/reports", 200,
            "departments", [department],
            "List financial reports permitted to the user"
        ),
        scenario(
            user, "finance", "/customers",
            200 if user == "Jodson" else 403,
            "count", 2 if user == "Jodson" else None,
            "Access customer contracts"
        ),
    ])


DENIED_REQUESTS = [
    ("Victoria", "documents", "/documents/2",
     "Read Felipe's confidential document"),
    ("Victoria", "hr", "/employees/Felipe",
     "Read Felipe's employee profile"),
    ("Victoria", "finance", "/reports/Finance",
     "Read Finance department report"),

    ("Felipe", "documents", "/documents/3",
     "Read Jodson's confidential document"),
    ("Felipe", "hr", "/employees/Jodson",
     "Read Jodson's employee profile"),
    ("Felipe", "finance", "/reports/Engineering",
     "Read Engineering department report"),

    ("Jodson", "documents", "/documents/2",
     "Read Felipe's confidential document"),
    ("Jodson", "hr", "/employees/Victoria",
     "Read Victoria's employee profile"),
    ("Jodson", "finance", "/reports/Engineering",
     "Read Engineering department report"),
]

for user, service, path, description in DENIED_REQUESTS:
    SCENARIOS.append(
        scenario(user, service, path, 403,
                 description=description)
    )


for user, department in USERS.items():
    SCENARIOS.extend([
        scenario(
            user, "hr", f"/employees/{user}", 200,
            "name", user,
            "Read own employee profile"
        ),
        scenario(
            user, "finance", f"/reports/{department}", 200,
            "department", department,
            "Read own department report"
        ),
    ])


SCENARIOS.extend([
    scenario(
        None, "documents", "/documents", 400,
        description="Reject missing user identity"
    ),
    scenario(
        "Unknown", "hr", "/employees", 400,
        description="Reject unknown user identity"
    ),
])


def check_response(data, field, expected):
    if field is None:
        return True

    if field == "ids":
        actual = sorted(item["id"] for item in data)
        return actual == sorted(expected)

    if field == "names":
        actual = sorted(item["name"] for item in data)
        return actual == sorted(expected)

    if field == "departments":
        actual = sorted(item["department"] for item in data)
        return actual == sorted(expected)

    if field == "count":
        return len(data) == expected

    return data.get(field) == expected


def run_scenario(client, test):
    service = test["service"]
    url = BASE_URLS[service] + test["path"]

    headers = {}
    if test["user"] is not None:
        headers["X-Acting-User"] = test["user"]

    result = {
        "user": test["user"] or "None",
        "service": service,
        "path": test["path"],
        "description": test["description"],
        "expected_status": test["expected_status"],
        "actual_status": None,
        "data_check": None,
        "passed": False,
        "error": None,
    }

    try:
        response = client.get(url, headers=headers)
        result["actual_status"] = response.status_code

        status_ok = response.status_code == test["expected_status"]
        data_ok = True

        if status_ok and response.status_code == 200:
            data = response.json()
            data_ok = check_response(
                data,
                test["field"],
                test["expected_value"]
            )
            result["data_check"] = data_ok

        result["passed"] = status_ok and data_ok

        if not status_ok:
            result["error"] = (
                f"Expected HTTP {test['expected_status']}, "
                f"received HTTP {response.status_code}"
            )
        elif not data_ok:
            result["error"] = "Returned data did not match expected data"

    except Exception as error:
        result["error"] = str(error)

    return result


def generate_markdown(report):
    results = report["results"]
    total = len(results)
    passed = sum(1 for result in results if result["passed"])
    failed = total - passed

    lines = [
        "# Stage 1 — Simple Authorization",
        "",
        f"- **Date:** {report['timestamp']}",
        "- **Test type:** API integration tests",
        "- **Identity mechanism:** X-Acting-User header",
        "- **Authorization:** Local policy checks",
        f"- **Total tests:** {total}",
        f"- **Passed:** {passed}",
        f"- **Failed:** {failed}",
        f"- **Pass rate:** {passed / total * 100:.1f}%",
        "",
        "## Test results",
        "",
        "| User | Service | Request | Expected | Actual | Result |",
        "|---|---|---|---:|---:|---|",
    ]

    for result in results:
        lines.append(
            f"| {result['user']} "
            f"| {result['service']} "
            f"| `{result['path']}` "
            f"| {result['expected_status']} "
            f"| {result['actual_status']} "
            f"| {'PASS' if result['passed'] else 'FAIL'} |"
        )

    lines.extend(["", "## Failed tests", ""])

    failures = [r for r in results if not r["passed"]]

    if not failures:
        lines.append("No failed tests.")
    else:
        for failure in failures:
            lines.append(
                f"- **{failure['description']}** — "
                f"{failure['error'] or 'Data mismatch'}"
            )

    lines.extend([
        "",
        "## Methodology and limitations",
        "",
        "The APIs were tested directly over HTTP. The user identity "
        "was supplied through X-Acting-User.",
        "",
        "This stage trusts the identity header and does not "
        "cryptographically authenticate the user. A caller able "
        "to reach the API can potentially impersonate another user.",
        "",
        "These tests evaluate API authorization, not LLM tool selection "
        "or final-answer disclosure. Those require separate agent tests.",
        "",
    ])

    return "\n".join(lines)


def main():
    output_dir = Path("research/reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().astimezone().isoformat()
    filename_timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    results = []

    with httpx.Client(timeout=10) as client:
        for index, test in enumerate(SCENARIOS, start=1):
            result = run_scenario(client, test)
            results.append(result)

            status = "PASS" if result["passed"] else "FAIL"
            print(
                f"[{status}] {index}/{len(SCENARIOS)} "
                f"{result['user']} {result['service']}"
                f"{result['path']}"
            )

            if result["error"]:
                print(f"       {result['error']}")

    passed = sum(1 for result in results if result["passed"])
    failed = len(results) - passed

    report = {
        "stage": 1,
        "name": "Simple Authorization",
        "timestamp": timestamp,
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "results": results,
    }

    json_path = output_dir / (
        f"stage-1-{filename_timestamp}.json"
    )
    md_path = output_dir / (
        f"stage-1-{filename_timestamp}.md"
    )

    json_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8"
    )

    md_path.write_text(
        generate_markdown(report),
        encoding="utf-8"
    )

    print("\n--- SUMMARY ---")
    print(f"Total:  {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"\nJSON report: {json_path}")
    print(f"Markdown report: {md_path}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
