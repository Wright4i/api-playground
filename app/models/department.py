from sqlalchemy import Column, CHAR, String
from sqlalchemy.orm import relationship, Session
from app.connections.base import Base  # Updated import
from pydantic import BaseModel
from typing import Optional

class Department(Base):
    __tablename__ = 'DEPARTMENT'
    id = Column(CHAR(3), primary_key=True,)
    name = Column(String(29), nullable=False)
    manager = Column(CHAR(6))
    location = Column(CHAR(16))
    employees = relationship("app.models.employee.Employee", order_by="app.models.employee.Employee.id", back_populates="department")

    @staticmethod
    def get_paginated(db: Session, page: Optional[int], limit: Optional[int]):
        if page is not None and limit is not None:
            skip = (page - 1) * limit
        else:
            skip = 0
            limit = None  # No limit
        query = db.query(Department).offset(skip)
        if limit is not None:
            query = query.limit(limit)
        departments = query.all()
        total_departments = db.query(Department).count()
        total_pages = (total_departments + limit - 1) // limit if limit is not None else 1
        return departments, total_departments, total_pages

    @staticmethod
    def get_by_id(db: Session, deptno: str):
        return db.query(Department).filter(Department.id == deptno).first()

    @staticmethod
    def update(db: Session, deptno: str, department_update: 'DepartmentUpdate'):
        db_department = db.query(Department).filter(Department.id == deptno).first()
        if db_department:
            for key, value in department_update.dict().items():
                setattr(db_department, key, value)
            db.commit()
            db.refresh(db_department)
        return db_department

    @staticmethod
    def create(db: Session, department_data: 'DepartmentUpdate'):
        new_department = Department(**department_data.dict())
        db.add(new_department)
        db.commit()
        db.refresh(new_department)
        return new_department

class DepartmentUpdate(BaseModel):
    id: str
    name: str
    manager: Optional[str] = None
    location: Optional[str] = None

class DepartmentSchema(BaseModel):
    id: str
    name: str
    manager: Optional[str] = None
    location: Optional[str] = None

    class Config:
        orm_mode = True
