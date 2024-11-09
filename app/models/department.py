from sqlalchemy import Column, CHAR, String
from sqlalchemy.orm import relationship, Session
from app.connections.base import Base  # Updated import
from pydantic import BaseModel
from typing import Optional

class Department(Base):
    __tablename__ = 'DEPARTMENT'
    DEPTNO = Column(CHAR(3), primary_key=True)
    DEPTNAME = Column(String(29), nullable=False)
    MGRNO = Column(CHAR(6))
    ADMRDEPT = Column(CHAR(3), nullable=False)
    LOCATION = Column(CHAR(16))
    employees = relationship("app.models.employee.Employee", order_by="app.models.employee.Employee.EMPNO", back_populates="department")  # Update relationship

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
        return db.query(Department).filter(Department.DEPTNO == deptno).first()

    @staticmethod
    def update(db: Session, deptno: str, department_update: 'DepartmentUpdate'):
        db_department = db.query(Department).filter(Department.DEPTNO == deptno).first()
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
    DEPTNO: str
    DEPTNAME: str
    MGRNO: Optional[str] = None
    ADMRDEPT: str
    LOCATION: Optional[str] = None

class DepartmentSchema(BaseModel):
    DEPTNO: str
    DEPTNAME: str
    MGRNO: Optional[str] = None
    ADMRDEPT: str
    LOCATION: Optional[str] = None

    class Config:
        orm_mode = True
