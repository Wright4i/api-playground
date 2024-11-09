from fastapi import Header
from app.models.token import Token

async def validate_token(tokens_db, authorization: str = Header(None)):
    if authorization and isinstance(authorization, str) and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        query = Token.__table__.select().where(Token.token == token)
        user = await tokens_db.fetch_one(query)
        if user:
            return {"status": "VALID", "username": user["name"]}
    return {"status": "INVALID", "username": None}
