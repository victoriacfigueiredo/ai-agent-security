
from fastapi import Header, HTTPException

USERS = {
    "Victoria": {"department": "Engineering"},
    "Felipe": {"department": "Human Resources"},
    "Jodson": {"department": "Finance"},
}


def get_acting_user(x_acting_user: str | None = Header(default=None)):
    """
    Stage 1 identity assertion.
    This header is trusted, not cryptographically authenticated.
    """
    if not x_acting_user or x_acting_user not in USERS:
        raise HTTPException(
            status_code=400,
            detail="Missing or unknown acting user"
        )

    return x_acting_user


def can_read_document(user, document):
    return (
        document["classification"] == "internal"
        or document["owner"] == user
    )


def can_read_employee(user, employee):
    return employee["name"] == user


def can_read_report(user, report):
    return report["department"] == USERS[user]["department"]


def can_read_customers(user):
    return USERS[user]["department"] == "Finance"
