
from fastapi import FastAPI, Depends, HTTPException
from data.seed import EMPLOYEES
from apis.policy import get_acting_user, can_read_employee

app = FastAPI(title="HR API - Stage 1")


@app.get("/employees")
def get_employees(user: str = Depends(get_acting_user)):
    return [
        employee for employee in EMPLOYEES
        if can_read_employee(user, employee)
    ]


@app.get("/employees/{employee_name}")
def get_employee(
    employee_name: str,
    user: str = Depends(get_acting_user)
):
    employee = next(
        (e for e in EMPLOYEES
         if e["name"].lower() == employee_name.lower()),
        None
    )

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    if not can_read_employee(user, employee):
        raise HTTPException(status_code=403, detail="Access denied")

    return employee
