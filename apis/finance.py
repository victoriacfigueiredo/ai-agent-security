from fastapi import FastAPI, Depends, HTTPException
from data.seed import FINANCIAL_REPORTS, CUSTOMERS
from apis.auth import require_role

app = FastAPI(title="Finance API - Stage 2 OAuth2")


@app.get("/reports")
def get_financial_reports(
    claims: dict = Depends(require_role("finance"))
):
    return FINANCIAL_REPORTS


@app.get("/reports/{department}")
def get_department_report(
    department: str,
    claims: dict = Depends(require_role("finance"))
):
    report = next(
        (r for r in FINANCIAL_REPORTS
         if r["department"].lower() == department.lower()),
        None
    )

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    return report


@app.get("/customers")
def get_customers(
    claims: dict = Depends(require_role("customers"))
):
    return CUSTOMERS
