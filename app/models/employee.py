from sqlalchemy import Column, CHAR, String, Date, Integer, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship, Session
from app.connections.base import Base  # Updated import
from typing import Optional
from pydantic import BaseModel
from datetime import date
from decimal import Decimal

class Employee(Base):
    __tablename__ = 'EMPLOYEE'
    id = Column(CHAR(6), primary_key=True)
    first = Column(String(12), nullable=False)
    last = Column(String(15), nullable=False)
    job = Column(String(8), nullable=False)
    workdept = Column(CHAR(3), ForeignKey('DEPARTMENT.id'))
    salary = Column(DECIMAL(9, 2))

    department = relationship("app.models.department.Department", back_populates="employees")

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = None):
        query = db.query(Employee).offset(skip)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def get_count(db: Session):
        return db.query(Employee).count()

    @staticmethod
    def get_by_id(db: Session, empno: str):
        return db.query(Employee).filter(Employee.id == empno).first()

    @staticmethod
    def update(db: Session, empno: str, employee_update: 'EmployeeUpdate'):
        db_employee = db.query(Employee).filter(Employee.id == empno).first()
        if db_employee:
            for key, value in employee_update.dict().items():
                setattr(db_employee, key, value)
            db.commit()
            db.refresh(db_employee)
        return db_employee

    @staticmethod
    def get_paginated(db: Session, page: Optional[int], limit: Optional[int]):
        if page is not None and limit is not None:
            skip = (page - 1) * limit
        else:
            skip = 0
            limit = None  # No limit
        employees = Employee.get_all(db, skip=skip, limit=limit)
        total_employees = Employee.get_count(db)
        total_pages = (total_employees + limit - 1) // limit if limit is not None else 1
        return employees, total_employees, total_pages

class EmployeeUpdate(BaseModel):
    first: Optional[str]
    last: Optional[str]
    job: Optional[str]
    workdept: Optional[str]
    salary: Optional[Decimal]

class EmployeeSchema(BaseModel):
    id: str
    first: str
    last: str
    job: str
    workdept: Optional[str]
    salary: Optional[Decimal]

    class Config:
        orm_mode = True
