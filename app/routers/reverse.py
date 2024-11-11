from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from app.templates import templates
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import requests
import json
import socket
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

router = APIRouter()
# Define ReverseRequest model
class ReverseRequest(BaseModel):
    url: str
    method: str
    headers: dict
    body: Optional[str] = None

def is_local_address(url: str) -> bool:
    local_addresses = []
    local_addresses.append(f"localhost:{os.getenv('PORT')}")
    local_addresses.append(f"127.0.0.1:{os.getenv('PORT')}")
    local_addresses.append(f"[::1]:{os.getenv('PORT')}")
    local_addresses.append(f"{os.getenv('HOST')}:{os.getenv('PORT')}")  
    return any(local_address in url for local_address in local_addresses)

@router.put("/reverse/")
async def reverse_api_call(reverse_request: ReverseRequest):
    
    # Ensure the URL includes the schema
    if not reverse_request.url.startswith(("http://", "https://")):
        reverse_request.url = "http://" + reverse_request.url

    # Prevent calling the same server
    if is_local_address(reverse_request.url):
        raise HTTPException(status_code=400, detail="Cannot call the same server")

    try:
        headers = reverse_request.headers
        if reverse_request.method.upper() == "GET":
            response = requests.get(reverse_request.url, headers=headers, timeout=10)
        elif reverse_request.method.upper() == "PUT":
            if headers.get("Content-Type") == "application/json":
                response = requests.put(reverse_request.url, json=json.loads(reverse_request.body), headers=headers, timeout=10)
            else:
                response = requests.put(reverse_request.url, data=reverse_request.body, headers=headers, timeout=10)
        elif reverse_request.method.upper() == "PATCH":
            if headers.get("Content-Type") == "application/json":
                response = requests.patch(reverse_request.url, json=json.loads(reverse_request.body), headers=headers, timeout=10)
            else:
                response = requests.patch(reverse_request.url, data=reverse_request.body, headers=headers, timeout=10)
        else:
            raise HTTPException(status_code=400, detail="Invalid request method")
        
        content_type = response.headers.get('Content-Type')
        if content_type and 'application/json' in content_type:
            try:
                content = response.json()
            except json.JSONDecodeError:
                content = response.text
        else:
            content = response.text
        
        return {"status_code": response.status_code, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.get("/reverse", response_class=HTMLResponse)
async def reverse_form(request: Request):
    return templates.TemplateResponse("reverse.html", {"request": request})