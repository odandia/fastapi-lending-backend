from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Session
from database.db import Base
from pydantic import BaseModel

class LoanSchemaBase(BaseModel):
    amount: int
    term: int
    interest_rate: int
    status: str

class LoanSchema(LoanSchemaBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer)
    term = Column(Integer)
    interest_rate = Column(Integer)
    status = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="loans")

def get_loan_by_id(db: Session, id: int):
    return db.query(Loan).filter(Loan.id == id).first()

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
