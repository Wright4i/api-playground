from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.employee import Employee, EmployeeUpdate, EmployeeSchema
from app.models.department import Department  # Add this import
from app.connections.sqlite import get_db, serialize_model
from app.routers.websocket import manager
from app.utils import validate_token
import json

router = APIRouter(
    prefix="/employees",
    tags=["employees"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=Dict[str, Any])
async def read_employees(request: Request, response: Response, page: Optional[int] = Query(None), limit: Optional[int] = Query(None), db: Session = Depends(get_db)):
    employees, total_employees, total_pages = Employee.get_paginated(db, page, limit)
    response.body = json.dumps({
        "employees": [serialize_model(emp) for emp in employees],
        "totalPages": total_pages,
        "totalRows": total_employees
    }).encode("utf-8")
    
    authorization = request.headers.get("Authorization", None)
    token_status = await validate_token(db, authorization)
    
    message_data = {
        "method": "GET",
        "uri": str(request.url),
        "status_code": 200,
        "sender": request.client.host,
        "authorization": authorization if authorization else "-",
        "authorization_status": token_status["status"],
        "username": token_status["username"] if token_status["status"] == "VALID" else "-",
        "request_body": (await request.body()).decode("utf-8"),
        "response_body": response.body.decode("utf-8") if response.body else "-"
    }
    await manager.broadcast(json.dumps(message_data))
    
    return {"employees": employees, "totalPages": total_pages, "totalRows": total_employees}

@router.get("/{id}", response_model=EmployeeSchema)
async def read_employee(request: Request, response: Response, id: str, db: Session = Depends(get_db)):
    employee = Employee.get_by_id(db, id)
    if not employee:
        response.body = json.dumps({"detail": "Employee not found"}).encode("utf-8")
        
        authorization = request.headers.get("Authorization", None)
        token_status = await validate_token(db, authorization)
        
        message_data = {
            "method": "GET",
            "uri": str(request.url),
            "status_code": 404,
            "sender": request.client.host,
            "authorization": authorization if authorization else "-",
            "authorization_status": token_status["status"],
            "username": token_status["username"] if token_status["status"] == "VALID" else "-",
            "request_body": (await request.body()).decode("utf-8"),
            "response_body": response.body.decode("utf-8") if response.body else "-"
        }
        await manager.broadcast(json.dumps(message_data))
        
        raise HTTPException(status_code=404, detail="Employee not found")
    response.body = json.dumps(serialize_model(employee)).encode("utf-8")
    
    authorization = request.headers.get("Authorization", None)
    token_status = await validate_token(db, authorization)
    
    message_data = {
        "method": "GET",
        "uri": str(request.url),
        "status_code": 200,
        "sender": request.client.host,
        "authorization": authorization if authorization else "-",
        "authorization_status": token_status["status"],
        "username": token_status["username"] if token_status["status"] == "VALID" else "-",
        "request_body": (await request.body()).decode("utf-8"),
        "response_body": response.body.decode("utf-8") if response.body else "-"
    }
    await manager.broadcast(json.dumps(message_data))
    
    return employee

@router.put("/", response_model=EmployeeSchema)
async def create_employee(request: Request, response: Response, employee: EmployeeUpdate, db: Session = Depends(get_db)):
    # Generate new employee number
    max_empno = db.query(Employee).order_by(Employee.id.desc()).first().id
    new_empno = str(int(max_empno) + 1)
    
    # Validate department number
    if employee.workdept and not db.query(Department).filter(Department.id == employee.workdept).first():
        raise HTTPException(status_code=400, detail="Invalid department number")
    
    # Create new employee
    new_employee = Employee(
        id=new_empno,
        first=employee.first,
        last=employee.last,
        job=employee.job,
        workdept=employee.workdept,
        salary=employee.salary
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    
    response.body = json.dumps(serialize_model(new_employee)).encode("utf-8")
    
    authorization = request.headers.get("Authorization", None)
    token_status = await validate_token(db, authorization)
    
    message_data = {
        "method": "PUT",
        "uri": str(request.url),
        "status_code": 201,
        "sender": request.client.host,
        "authorization": authorization if authorization else "-",
        "authorization_status": token_status["status"],
        "username": token_status["username"] if token_status["status"] == "VALID" else "-",
        "request_body": (await request.body()).decode("utf-8"),
        "response_body": response.body.decode("utf-8") if response.body else "-"
    }
    await manager.broadcast(json.dumps(message_data))
    
    response.status_code = 201  # Update the status code to match the broadcasted status code
    return new_employee

@router.patch("/{id}", response_model=EmployeeSchema)
async def patch_employee(request: Request, response: Response, id: str, employee: EmployeeUpdate, db: Session = Depends(get_db)):
    # Validate department number
    if employee.workdept and not db.query(Department).filter(Department.id == employee.workdept).first():
        raise HTTPException(status_code=400, detail="Invalid department number")
    
    db_employee = Employee.update(db, id, employee)
    if db_employee is None:
        response.body = json.dumps({"detail": "Employee not found"}).encode("utf-8")
        
        authorization = request.headers.get("Authorization", None)
        token_status = await validate_token(db, authorization)
        
        message_data = {
            "method": "PATCH",
            "uri": str(request.url),
            "status_code": 404,
            "sender": request.client.host,
            "authorization": authorization if authorization else "-",
            "authorization_status": token_status["status"],
            "username": token_status["username"] if token_status["status"] == "VALID" else "-",
            "request_body": (await request.body()).decode("utf-8"),
            "response_body": response.body.decode("utf-8") if response.body else "-"
        }
        await manager.broadcast(json.dumps(message_data))
        
        raise HTTPException(status_code=404, detail="Employee not found")
    response.body = json.dumps(serialize_model(db_employee)).encode("utf-8")
    
    authorization = request.headers.get("Authorization", None)
    token_status = await validate_token(db, authorization)
    
    message_data = {
        "method": "PATCH",
        "uri": str(request.url),
        "status_code": 200,
        "sender": request.client.host,
        "authorization": authorization if authorization else "-",
        "authorization_status": token_status["status"],
        "username": token_status["username"] if token_status["status"] == "VALID" else "-",
        "request_body": (await request.body()).decode("utf-8"),
        "response_body": response.body.decode("utf-8") if response.body else "-"
    }
    await manager.broadcast(json.dumps(message_data))
    
    return db_employee

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "CONNECT", "TRACE"])
async def echo_all(request: Request, response: Response, db: Session = Depends(get_db)):
    
    authorization = request.headers.get("Authorization", None)
    token_status = await validate_token(db, authorization)
    
    message_data = {
        "method": request.method,
        "uri": str(request.url),
        "status_code": 405,
        "sender": request.client.host,
        "authorization": authorization if authorization else "-",
        "authorization_status": token_status["status"],
        "username": token_status["username"] if token_status["status"] == "VALID" else "-",
        "request_body": (await request.body()).decode("utf-8"),
        "response_body": response.body.decode("utf-8") if response.body else "-"
    }
    await manager.broadcast(json.dumps(message_data))
    
    response.status_code = 405
    return response