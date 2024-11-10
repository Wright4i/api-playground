import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import databases
from faker import Faker
from app.models.department import Department
from app.models.employee import Employee
from app.connections.base import Base, metadata  # Updated import

# Ensure the database directory exists
db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db')
os.makedirs(db_dir, exist_ok=True)

# Ensure the unified database file exists
db_file = os.path.join(db_dir, 'sqlite.db')
if not os.path.exists(db_file):
    open(db_file, 'w', encoding='utf-8').close()

DATABASE_URL = f"sqlite:///{db_file}"
database = databases.Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def serialize_model(model):
    return {column.name: str(getattr(model, column.name)) for column in model.__table__.columns}

def create_tables():
    Base.metadata.create_all(bind=engine)

def drop_tables():
    Base.metadata.drop_all(bind=engine)

def generate_employee_data(db, fake, empno_counter):
    employees = []
    for _ in range(50):
        emp = Employee(
            id=str(empno_counter),  # Use sequential id
            first=fake.first_name(),
            last=fake.last_name(),
            job=fake.job(),
            workdept=None,
            salary=fake.random_number(digits=5)
        )
        db.add(emp)
        employees.append(emp)
        empno_counter += 1  # Increment id for the next employee
    db.commit()
    return employees

def generate_department_data(db, fake, employees):
    department_data = [
        ('IT', 'Information Technology'),
        ('HR', 'Human Resources'),
        ('FIN', 'Finance'),
        ('MKT', 'Marketing'),
        ('OPS', 'Operations'),
        ('R&D', 'Research and Development'),
        ('QA', 'Quality Assurance'),
        ('MIS', 'Management Information Systems'),
        ('CS', 'Customer Service'),
        ('ADM', 'Administration')
    ]

    departments = []
    for abbr, name in department_data:
        mgrno = fake.random_element(elements=[emp.id for emp in employees]) if employees else None
        dept = Department(
            id=abbr,
            name=name,
            manager=mgrno,
            location=fake.city()
        )
        db.add(dept)
        departments.append(dept)
    db.commit()
    return departments

def generate_fake_data(generate_employees=True, generate_departments=True):
    fake = Faker()
    db = SessionLocal()
    empno_counter = 101
    try:
        employees = []
        departments = []

        if generate_employees:
            employees = generate_employee_data(db, fake, empno_counter)
        else:
            employees = db.query(Employee).all()
            if not employees:
                employees = generate_employee_data(db, fake, empno_counter)

        if generate_departments:
            departments = generate_department_data(db, fake, employees)
        else:
            departments = db.query(Department).all()
            if not departments:
                departments = generate_department_data(db, fake, employees)

        for emp in employees:
            emp.workdept = fake.random_element(elements=[dept.id for dept in departments])
        db.commit()

    except Exception as e:
        db.rollback()
    finally:
        db.close()

def reset_database():
    drop_tables()
    create_tables()
    generate_fake_data()