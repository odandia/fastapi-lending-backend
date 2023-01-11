from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, Session
from database.db import Base
from pydantic import BaseModel
from fastapi import HTTPException

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)

    username = Column(String)

    loans = relationship("Loan", back_populates="owner")
    shared_loans = relationship("Loan", secondary="loan_access", back_populates="users")

class UserSchemaBase(BaseModel):
    username: str

class UserSchema(UserSchemaBase):
    id: int

    class Config:
        orm_mode = True

def validate_user(userData: UserSchemaBase):
    '''
    Validate the input data for user creation
    Returns:
        HTTPException if validation fails
        None otherwise
    '''
    if not isinstance(userData.username, str):
        return HTTPException(status_code=400, detail="Username must be a string" )
    if len(userData.username) < 3:
        return HTTPException(status_code=400, detail="Username must be at least 3 characters")
    return None

def create_user(db: Session, userData: UserSchemaBase):
    db_user = User(**userData.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, id: int):
    return db.query(User).filter(User.id == id).first()

def get_users(db: Session, skip: int=0, limit: int=100):
    return db.query(User).offset(skip).limit(limit).all()