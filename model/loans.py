from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship, Session
from database.db import Base
from pydantic import BaseModel
from fastapi import HTTPException

class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True, index=True)

    amount = Column(Float)
    apr = Column(Float)
    term = Column(Integer)
    status = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="loans")

class LoanSchemaBase(BaseModel):
    amount: float
    apr: float
    term: int
    status: str = "active"
    owner_id: int

class LoanSchema(LoanSchemaBase):
    id: int

    class Config:
        orm_mode = True

class LoanScheduleSchema(BaseModel):
    month: int
    open_balance: float
    total_payment: float
    principal_payment: float
    interest_payment: float
    close_balance: float

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
    if not isinstance(loan.apr, float):
        return HTTPException(status_code=400, detail="Loan interest_rate must be a float" )
    if loan.apr <= 0:
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

def update_loan(db: Session, loan: Loan, loanData: LoanSchemaBase):
    # I'm not sure why VSCode doesn't like these -- runs fine
    # I can get rid of the red squigglies by adding type hints to the attributes
    # in the Loan constructor... but then it complains about the type hints
    loan.amount = loanData.amount
    loan.apr = loanData.apr
    loan.term = loanData.term
    loan.status = loanData.status
    loan.owner_id = loanData.owner_id
    db.commit()
    db.refresh(loan)
    return loan

def get_loan_by_id(db: Session, id: int) -> Loan | None :
    return db.query(Loan).filter(Loan.id == id).first()

def get_loans_by_owner_id(db: Session, owner_id: int, skip: int=0, limit: int=100):
    return db.query(Loan).filter(Loan.owner_id == owner_id).offset(skip).limit(limit).all()

def calc_monthly_interest(apr: float, balance: float):
    return balance * apr / 12

# TODO: add some caching to these? may get called often for the same params
def calc_monthly_total_payment(apr: float, balance: float, term: int):
    # monthly_interest_payment = calc_monthly_interest(apr, balance)
    temp_val = ((apr / 12) + 1) ** term
    return balance * ((apr / 12 * temp_val) / (temp_val - 1))

# ^^calls like these, could definitely use some DP
def calc_monthly_principal_payment(apr: float, balance: float, term: int):
    return calc_monthly_total_payment(apr, balance, term) - calc_monthly_interest(apr, balance)

def get_loan_schedule_for_loan(loan: LoanSchema):
    return get_loan_schedule(loan.apr, loan.amount, loan.term)

def get_loan_schedule(apr: float, amount: float, term: int):
    schedule = []
    monthly_payment = calc_monthly_total_payment(apr, amount, term)
    principal = amount

    for month in range(1, term + 1):

        interest_amount = calc_monthly_interest(apr, principal)
        principal_payment = monthly_payment - interest_amount

        open_balance = principal
        principal -= principal_payment
        close_balance = principal

        schedule.append(LoanScheduleSchema(
            month=month, open_balance=open_balance, close_balance=close_balance, total_payment=monthly_payment,
            principal_payment=principal_payment, interest_payment=interest_amount)
        )

    return schedule

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
