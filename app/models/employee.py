from sqlalchemy import Column, CHAR, String, Date, Integer, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship, Session
from app.connections.base import Base  # Updated import
from typing import Optional
from pydantic import BaseModel
from datetime import date
from decimal import Decimal

class Employee(Base):
    __tablename__ = 'EMPLOYEE'
    EMPNO = Column(CHAR(6), primary_key=True)
    FIRSTNME = Column(String(12), nullable=False)
    MIDINIT = Column(CHAR(1), nullable=False)
    LASTNAME = Column(String(15), nullable=False)
    WORKDEPT = Column(CHAR(3), ForeignKey('DEPARTMENT.DEPTNO'))
    PHONENO = Column(CHAR(4))
    HIREDATE = Column(Date)
    JOB = Column(CHAR(8))
    EDLEVEL = Column(Integer, nullable=False)
    SEX = Column(CHAR(1))
    BIRTHDATE = Column(Date)
    SALARY = Column(DECIMAL(9, 2))
    BONUS = Column(DECIMAL(9, 2))
    COMM = Column(DECIMAL(9, 2))

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
        return db.query(Employee).filter(Employee.EMPNO == empno).first()

    @staticmethod
    def update(db: Session, empno: str, employee_update: 'EmployeeUpdate'):
        db_employee = db.query(Employee).filter(Employee.EMPNO == empno).first()
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
    FIRSTNME: Optional[str]
    MIDINIT: Optional[str]
    LASTNAME: Optional[str]
    WORKDEPT: Optional[str]
    PHONENO: Optional[str]
    HIREDATE: Optional[date]
    JOB: Optional[str]
    EDLEVEL: Optional[int]
    SEX: Optional[str]
    BIRTHDATE: Optional[date]
    SALARY: Optional[Decimal]
    BONUS: Optional[Decimal]
    COMM: Optional[Decimal]

class EmployeeSchema(BaseModel):
    EMPNO: str
    FIRSTNME: str
    MIDINIT: str
    LASTNAME: str
    WORKDEPT: Optional[str]
    PHONENO: Optional[str]
    HIREDATE: Optional[date]
    JOB: Optional[str]
    EDLEVEL: int
    SEX: str
    BIRTHDATE: date
    SALARY: Optional[Decimal]
    BONUS: Optional[Decimal]
    COMM: Optional[Decimal]

    class Config:
        orm_mode = True
