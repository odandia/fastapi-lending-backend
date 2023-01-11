from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import Session
from database.db import Base
from model.loans import Loan

class LoanAccess(Base):
    __tablename__ = "loan_access"
    loan_id = Column(Integer, ForeignKey('loans.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

def access_check(db: Session, loan_id: int, user_id: int):
    '''
    Check if a user has access to a loan
    Returns True/False
    '''
    return db.query(LoanAccess).filter(LoanAccess.loan_id == loan_id, LoanAccess.user_id == user_id).first() is not None

def add_user(db: Session, loan_id: int, user_id: int):
    '''
    Add access for the user to view the loan
    '''
    # succeed fast if the user already has access
    if access_check(db, loan_id, user_id):
        return True

    db_loan_access = LoanAccess(loan_id=loan_id, user_id=user_id)
    db.add(db_loan_access)
    db.commit()
    db.refresh(db_loan_access)
    return True

def get_loans_by_user_id(db: Session, user_id: int):
    '''
    Get a list of all loans a user has access to
    '''
    return db.query(Loan).join(LoanAccess, LoanAccess.loan_id == Loan.id).filter(LoanAccess.user_id == user_id).all()