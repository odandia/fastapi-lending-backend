from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship, Session
from database.db import Base
from pydantic import BaseModel
from fastapi import HTTPException


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    term = Column(Integer)
    interest_rate = Column(Float)
    status = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="loans")

class LoanSchemaBase(BaseModel):
    amount: float
    interest_rate: float
    term: int
    status: str
    owner_id: int

class LoanSchema(LoanSchemaBase):
    id: int

    class Config:
        orm_mode = True

def validateLoan(loan: LoanSchemaBase):
    '''
    Validate the input data for loan creation
    Returns:
        HTTPException if validation fails
        None otherwise
    '''
    if not isinstance(loan.amount, float):
        return HTTPException(status_code=400, detail="Loan amount must be a float" )
    if loan.amount <= 0:
        return HTTPException(status_code=400, detail="Loan amount must be greater than zero" )
    if not isinstance(loan.interest_rate, float):
        return HTTPException(status_code=400, detail="Loan interest_rate must be a float" )
    if loan.interest_rate <= 0:
        return HTTPException(status_code=400, detail="Loan interest_rate must be greater than zero" )
    if not isinstance(loan.term, int):
        return HTTPException(status_code=400, detail="Loan term must be an int (number of months)" )
    if loan.term <= 0:
        return HTTPException(status_code=400, detail="Loan term must be greater than zero" )
    if not isinstance(loan.status, str):
        return HTTPException(status_code=400, detail="Loan status must be a string" )
    if loan.status not in ["active", "inactive"]:
        return HTTPException(status_code=400, detail="Loan status must be either 'active' or 'inactive'" )
    if not isinstance(loan.owner_id, int):
        return HTTPException(status_code=400, detail="Loan owner_id must be an int" )
    else:
        return None

def create_loan(db: Session, loanData: LoanSchemaBase):
    db_loan = Loan(**loanData.dict())
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan

def get_loan_by_id(db: Session, id: int):
    return db.query(Loan).filter(Loan.id == id).first()

def get_loans_by_owner_id(db: Session, owner_id: int, skip: int=0, limit: int=100):
    return db.query(Loan).filter(Loan.owner_id == owner_id).offset(skip).limit(limit).all()

    # def __init__(self, id, amount,term, interest_rate, status):
    #     super().__init__(id=id, amount=amount, term=term, interest_rate=interest_rate, status=status)

    # def to_json(self):
    #     return {
    #         "id": self.id,
    #         "amount": self.amount,
    #         "term": self.term,
    #         "interest_rate": self.interest_rate,
    #         "status": self.status,
    #         "owner_id": self.owner_id,
    #     }

    # ## TODO: Amortized calculation
    # def calculate_interest(self):
    #     return self.amount * self.interest_rate * self.term
