from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query
from sqlalchemy.orm import Session
from app.connections.sqlite import get_db
from app.models.department import Department, DepartmentUpdate, DepartmentSchema
from typing import Optional, List
import json
from app.routers.websocket import manager
from app.utils import validate_token
from pydantic import BaseModel

router = APIRouter(
    prefix="/departments",
    tags=["departments"],
    responses={404: {"description": "Not found"}},
)

def serialize_model(model):
    return {column.name: str(getattr(model, column.name)) for column in model.__table__.columns}

class PaginatedDepartments(BaseModel):
    departments: List[DepartmentSchema]
    totalPages: int
    totalRows: int

async def broadcast_message(db, request, response, method, status_code):
    authorization = request.headers.get("Authorization", None)
    token_status = await validate_token(db, authorization)
    
    message_data = {
        "method": method,
        "uri": str(request.url),
        "status_code": status_code,
        "sender": request.client.host,
        "authorization": authorization if authorization else "-",
        "authorization_status": token_status["status"],
        "username": token_status["username"] if token_status["status"] == "VALID" else "-",
        "request_body": (await request.body()).decode("utf-8"),
        "response_body": response.body.decode("utf-8") if response.body else "-"
    }
    await manager.broadcast(json.dumps(message_data))

@router.get("/", response_model=PaginatedDepartments)
async def read_departments(request: Request, response: Response, page: Optional[int] = Query(None), limit: Optional[int] = Query(None), db: Session = Depends(get_db)):  # Update the function signature
    if page is not None and limit is not None:
        skip = (page - 1) * limit
    else:
        skip = 0
        limit = None  # No limit

    departments, total_departments, total_pages = Department.get_paginated(db, page, limit)
    response.body = json.dumps({
        "departments": [serialize_model(dept) for dept in departments],
        "totalPages": total_pages,
        "totalRows": total_departments
    }).encode("utf-8")
    await broadcast_message(db, request, response, "GET", 200)
    return {
        "departments": departments,
        "totalPages": total_pages,
        "totalRows": total_departments
    }

@router.get("/{id}", response_model=DepartmentSchema)
async def read_department(request: Request, response: Response, id: str, db: Session = Depends(get_db)):  # Update the function signature
    department = Department.get_by_id(db, id)
    if department is None:
        response.body = json.dumps({"detail": "Department not found"}).encode("utf-8")
        await broadcast_message(db, request, response, "GET", 404)
        raise HTTPException(status_code=404, detail="Department not found")
    response.body = json.dumps(serialize_model(department)).encode("utf-8")
    await broadcast_message(db, request, response, "GET", 200)
    return department

@router.put("/", response_model=DepartmentSchema)
async def create_department(request: Request, response: Response, department: DepartmentUpdate, db: Session = Depends(get_db)):  # Update the function signature
    if not department.DEPTNO:
        response.body = json.dumps({"detail": "Department number is required"}).encode("utf-8")
        await broadcast_message(db, request, response, "PUT", 400)
        raise HTTPException(status_code=400, detail="Department number is required")

    existing_department = Department.get_by_id(db, department.DEPTNO)
    if existing_department:
        response.body = json.dumps({"detail": "Department number must be unique"}).encode("utf-8")
        await broadcast_message(db, request, response, "PUT", 400)
        raise HTTPException(status_code=400, detail="Department number must be unique")
    
    admin_department = Department.get_by_id(db, department.ADMRDEPT)
    if not admin_department:
        response.body = json.dumps({"detail": "Admin department must be a valid DEPTNO"}).encode("utf-8")
        await broadcast_message(db, request, response, "PUT", 400)
        raise HTTPException(status_code=400, detail="Admin department must be a valid DEPTNO")
    
    # Validate MGRNO is a valid Employee
    if department.MGRNO:
        from app.models.employee import Employee  # Import here to avoid circular import
        manager = db.query(Employee).filter(Employee.EMPNO == department.MGRNO).first()
        if not manager:
            response.body = json.dumps({"detail": "Manager number must be a valid EMPNO"}).encode("utf-8")
            await broadcast_message(db, request, response, "PUT", 400)
            raise HTTPException(status_code=400, detail="Manager number must be a valid EMPNO")
    
    new_department = Department.create(db, department)
    response.body = json.dumps(serialize_model(new_department)).encode("utf-8")
    await broadcast_message(db, request, response, "PUT", 201)
    response.status_code = 201  
    return new_department

@router.patch("/{id}", response_model=DepartmentSchema)
async def patch_department(request: Request, response: Response, id: str, department: DepartmentUpdate, db: Session = Depends(get_db)):  # Update the function signature
    db_department = Department.update(db, id, department)
    if db_department is None:
        response.body = json.dumps({"detail": "Department not found"}).encode("utf-8")
        await broadcast_message(db, request, response, "PATCH", 404)
        raise HTTPException(status_code=404, detail="Department not found")
    response.body = json.dumps(serialize_model(db_department)).encode("utf-8")
    await broadcast_message(db, request, response, "PATCH", 200)
    return db_department

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "CONNECT", "TRACE"])
async def echo_all(request: Request, response: Response, db: Session = Depends(get_db)):  # Update the function signature
    await broadcast_message(db, request, response, request.method, 405)
    response.status_code = 405
    return response