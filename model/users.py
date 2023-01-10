from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, Session
from database.db import Base
from pydantic import BaseModel

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)

    username = Column(String)

    loans = relationship("Loan", back_populates="owner")

class UserSchemaBase(BaseModel):
    username: str

class UserSchema(UserSchemaBase):
    id: int

    class Config:
        orm_mode = True

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