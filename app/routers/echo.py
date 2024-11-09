from fastapi import APIRouter, Request, Response, Depends
import json
from sqlalchemy.orm import Session
from app.utils import validate_token
from app.connections.sqlite import get_db 
from app.routers.websocket import manager, broadcast_message

router = APIRouter()

@router.api_route("/echo/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "CONNECT", "TRACE"])
async def echo_all(request: Request, response: Response, db: Session = Depends(get_db)): 
    body = await request.body()
    message = body.decode("utf-8")
    response_data = {
        "uri": str(request.url),
        "method": request.method,
        "body": message
    }
    
    authorization = request.headers.get("Authorization", None)
    token_status = await validate_token(db, authorization)
    
    broadcast_message_data = {
        "method": request.method,
        "uri": str(request.url),
        "status_code": 200,
        "sender": request.client.host,
        "authorization": authorization if authorization else "-",
        "authorization_status": token_status["status"],
        "username": token_status["username"] if token_status["status"] == "VALID" else "-",
        "request_body": message,
        "response_body": json.dumps(response_data)  # Include response body
    }
    await broadcast_message(json.dumps(broadcast_message_data))
    return response_data