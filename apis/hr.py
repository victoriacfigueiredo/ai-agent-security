from fastapi import FastAPI, Depends, HTTPException
from data.seed import EMPLOYEES
from apis.auth import require_role

app = FastAPI(title="HR API - Stage 2 OAuth2")


@app.get("/employees")
def get_employees(
    claims: dict = Depends(require_role("employees"))
):
    return EMPLOYEES


@app.get("/employees/{employee_name}")
def get_employee(
    employee_name: str,
    claims: dict = Depends(require_role("employees"))
):
    employee = next(
        (e for e in EMPLOYEES
         if e["name"].lower() == employee_name.lower()),
        None
    )

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee
