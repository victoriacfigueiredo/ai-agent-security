
from fastapi import FastAPI, Depends, HTTPException
from data.seed import FINANCIAL_REPORTS, CUSTOMERS
from apis.policy import (
    get_acting_user,
    can_read_report,
    can_read_customers
)

app = FastAPI(title="Finance API - Stage 1")


@app.get("/reports")
def get_financial_reports(user: str = Depends(get_acting_user)):
    return [
        report for report in FINANCIAL_REPORTS
        if can_read_report(user, report)
    ]


@app.get("/reports/{department}")
def get_department_report(
    department: str,
    user: str = Depends(get_acting_user)
):
    report = next(
        (r for r in FINANCIAL_REPORTS
         if r["department"].lower() == department.lower()),
        None
    )

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    if not can_read_report(user, report):
        raise HTTPException(status_code=403, detail="Access denied")

    return report


@app.get("/customers")
def get_customers(user: str = Depends(get_acting_user)):
    if not can_read_customers(user):
        raise HTTPException(status_code=403, detail="Access denied")

    return CUSTOMERS
