from fastapi import FastAPI, Request, HTTPException, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from app.routers import token, echo, reverse, websocket, employee, department
from dotenv import load_dotenv
from app.connections.sqlite import Base, engine, get_db, reset_database, generate_fake_data
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text
from sqlalchemy.orm import Session
import os
import json
from app.utils import validate_token
from app.templates import templates

load_dotenv()

app = FastAPI()

# Include routers
app.include_router(token.router)
app.include_router(echo.router)
app.include_router(reverse.router)
app.include_router(websocket.router)  # Ensure this line is present
app.include_router(employee.router)
app.include_router(department.router)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create database tables
Base.metadata.create_all(bind=engine)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    host = os.getenv("HOST", "localhost")
    port = os.getenv("PORT", "10500")
    python_link = os.getenv("PYTHON_LINK", "https://github.com/wright4i")
    php_link = os.getenv("PHP_LINK", "https://github.com/p-behr")
    node_link = os.getenv("NODE_LINK", "https://github.com/worksofliam")
    swagger_link = os.getenv("SWAGGER_LINK", "https://editor.swagger.io/")
    admin_pass = os.getenv("ADMIN_PASS", "admin")
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "host": host, 
        "port": port,
        "node_link": node_link,
        "php_link": php_link,
        "python_link": python_link,
        "swagger_link": swagger_link,
        "admin_pass": admin_pass
    })

@app.get("/requests", response_class=HTMLResponse)
async def requests_page(request: Request):
    return templates.TemplateResponse("requests.html", {"request": request})

@app.post("/admin/reset-employee")
async def reset_employee(db: Session = Depends(get_db)):
    db.execute(text("DELETE FROM EMPLOYEE"))
    db.commit()
    generate_fake_data(generate_departments=False)
    return {"message": "EMPLOYEE table reset successfully"}

@app.post("/admin/reset-department")
async def reset_department(db: Session = Depends(get_db)):
    db.execute(text("DELETE FROM DEPARTMENT"))
    db.commit()
    generate_fake_data(generate_employees=False)
    return {"message": "DEPARTMENT table reset successfully"}

@app.post("/admin/reset-token")
async def reset_token(db: Session = Depends(get_db)):
    db.execute(text("DELETE FROM tokens"))
    db.commit()
    # Add logic to re-populate tokens table if needed
    return {"message": "TOKEN table reset successfully"}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_body = await request.body()
    authorization = request.headers.get("authorization")
    token_info = await validate_token(authorization)
    message = {
        "method": request.method,
        "uri": str(request.url),
        "status_code": 422,
        "sender": request.client.host,
        "authorization": authorization,
        "authorization_status": token_info["status"],
        "username": token_info["username"],
        "content_type": request.headers.get("content-type"),
        "request_body": request_body.decode("utf-8"),
        "response_body": json.dumps({"detail": exc.errors()}),
        "db": "-"
    }
    await websocket.manager.broadcast(json.dumps(message))
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_body = await request.body()
    authorization = request.headers.get("authorization")
    token_info = await validate_token(authorization)
    message = {
        "method": request.method,
        "uri": str(request.url),
        "status_code": exc.status_code,
        "sender": request.client.host,
        "authorization": authorization,
        "authorization_status": token_info["status"],
        "username": token_info["username"],
        "content_type": request.headers.get("content-type"),
        "request_body": request_body.decode("utf-8"),
        "response_body": json.dumps({"detail": exc.detail}),
        "db": "-"
    }
    await websocket.manager.broadcast(json.dumps(message))
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.on_event("startup")
async def startup():
    reset_database()
    try:
        with engine.connect() as conn:  
            conn.execute(text("SELECT 1 FROM tokens LIMIT 1"))
    except OperationalError:
        Base.metadata.create_all(bind=engine) 
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1 FROM EMPLOYEE LIMIT 1"))
    except OperationalError:
        Base.metadata.create_all(bind=engine)
