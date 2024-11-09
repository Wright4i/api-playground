from sqlalchemy import Column, String
from sqlalchemy.orm import Session
from urllib.parse import quote, unquote
import uuid
from app.connections.sqlite import Base
from pydantic import BaseModel

class Token(Base):  # Use Base
    __tablename__ = "tokens"
    name = Column(String, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)

    @staticmethod
    def create(db: Session, name: str):
        name = quote(name, safe='')
        existing_user = db.query(Token).filter(Token.name == name).first()
        if existing_user:
            return None
        token = str(uuid.uuid4())
        db_token = Token(name=name, token=token)
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        return token

    @staticmethod
    def delete(db: Session, name: str):
        name = unquote(name)
        existing_user = db.query(Token).filter(Token.name == quote(name, safe='')).first()
        if not existing_user:
            return False
        db.delete(existing_user)
        db.commit()
        return True

    @staticmethod
    def get_all(db: Session):
        return db.query(Token).all()

    @staticmethod
    def get_by_name(db: Session, name: str):
        name = unquote(name)
        return db.query(Token).filter(Token.name == quote(name, safe='')).first()
