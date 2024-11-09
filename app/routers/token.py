from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from app.connections.sqlite import get_db
from app.models.token import Token  
from app.templates import templates
from urllib.parse import unquote
from fastapi.responses import HTMLResponse
from fastapi import Request
from urllib.parse import quote

router = APIRouter()

class User(BaseModel):
    name: str

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name must not be empty or only spaces')
        return v

@router.post("/auth/")
async def generate_token(user: User, db: Session = Depends(get_db)):
    user.name = quote(user.name, safe='')
    
    token = Token.create(db, user.name)
    if token is None:
        return {"message": f"{unquote(user.name)} already has a token."}
    return {"token": token}

@router.delete("/auth/{name}")
async def delete_token(name: str, db: Session = Depends(get_db)):
    name = unquote(name)
    
    if not Token.delete(db, name):
        raise HTTPException(status_code=404, detail="Token not found")
    return {"message": "Token deleted"}

@router.get("/auth/tokens")
async def get_tokens(db: Session = Depends(get_db)):
    tokens = Token.get_all(db)
    return tokens

@router.get("/auth/{name}")
async def get_token(name: str, db: Session = Depends(get_db)):
    name = unquote(name)
    
    token = Token.get_by_name(db, name)
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    return {"token": token.token}

@router.get("/auth", response_class=HTMLResponse)
async def auth_form(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})