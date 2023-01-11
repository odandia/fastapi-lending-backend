import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from typing import List
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from database.db import SessionLocal, engine, Base
from model import loans, users, loan_access

Base.metadata.create_all(bind=engine)

# TODO: API Versioning
# (quick solution at https://github.com/DeanWay/fastapi-versioning)
app = FastAPI(
    title="Lending API",
    description="API for managing loans",
    version="0.1",
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# redirect / to /docs
@app.get("/", response_class=RedirectResponse)
def redirect_to_docs():
    return "/docs"

@app.post("/users", response_model=users.UserSchema)
def create_user(userData: users.UserSchemaBase, db: Session = Depends(get_db)):
    err = users.validate_user(userData)
    if err:
        raise err

    return users.create_user(db=db, userData=userData)

@app.get("/users", response_model=List[users.UserSchema])
def list_users(db: Session = Depends(get_db)):
    return users.get_users(db=db)

@app.post("/loans", response_model=loans.LoanSchema)
def create_loan(loanData: loans.LoanSchemaBase, db: Session = Depends(get_db)):
    """
    Route to create a new loan
    Adds the owner to the loan access map
    """
    err = loans.validateLoan(loanData)
    if err:
        raise err

    owner = users.get_user_by_id(db=db, id=loanData.owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="User %d not found" % loanData.owner_id )

    loan = loans.create_loan(db=db, loanData=loanData)
    loan_access.add_user(db=db, loan_id=loan.id, user_id=loanData.owner_id)

    return loan

@app.get("/users/{user_id}/loans", response_model=List[loans.LoanSchema])
def list_user_loans(user_id: int, db: Session = Depends(get_db)):
    """
    Route to list all loans a user has access to
    This includes loans both owned by and shared with the user
    """
    user = users.get_user_by_id(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User %d not found" % user_id )

    return loan_access.get_loans_by_user_id(db=db, user_id=user_id)

@app.get("/loans/{loan_id}", response_model=List[loans.LoanScheduleSchema])
def get_loan_schedule(loan_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Route to return the full monthly loan schedule
    The loan must be owned by or shared with the user
    """
    # Maybe better to make these failed auth checks return 404s? To obfuscate the real IDs
    if not loan_access.access_check(db=db, loan_id=loan_id, user_id=user_id):
        raise HTTPException(status_code=403, detail="User %d does not have access to loan %d" % (user_id, loan_id) )

    loan = loans.get_loan_by_id(db=db, id=loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan %d not found" % loan_id )

    # Some funky math down this callstack, someone better versed with lending schedules should review
    return loans.get_loan_schedule_for_loan(loan)

@app.get("/loans/{loan_id}/month/{month}", response_model=loans.LoanSummarySchema)
def get_loan_summary(loan_id: int, month: int, user_id: int, db: Session = Depends(get_db)):
    """
    Route to return the loan summary for a given month
    The loan must be owned by or shared with the user
    """
    if not loan_access.access_check(db=db, loan_id=loan_id, user_id=user_id):
        raise HTTPException(status_code=403, detail="User %d does not have access to loan %d" % (user_id, loan_id) )

    loan = loans.get_loan_by_id(db=db, id=loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan %d not found" % loan_id )

    try:
        return loans.get_loan_summary_for_loan(loan, month)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/loans/{loan_id}", response_model=loans.LoanSchema)
def update_loan(loan_id: int, loan_data: loans.LoanSchemaBase, user_id: int, db: Session = Depends(get_db)):
    """
    Updates the loan at the provided loan_id with the new loan_data
    The loan must be owned by the user at user_id
    """
    err = loans.validateLoan(loan_data)
    if err:
        raise err

    loan = loans.get_loan_by_id(db=db, id=loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan %d not found" % loan_id )

    if not user_id == loan.owner_id:
        raise HTTPException(status_code=403, detail="User %d does not have access to update loan %d" % (user_id, loan_id) )

    return loans.update_loan(db=db, loan=loan, loanData=loan_data)

@app.post("/loans/{loan_id}/share")
def share_loan(loan_id: int, owner_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Route to share a loan with a user at user_id
    The loan must be owned by the user at owner_id
    """
    loan = loans.get_loan_by_id(db=db, id=loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan %d not found" % loan_id )

    user = users.get_user_by_id(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User %d not found" % user_id )

    if loan.owner_id != owner_id:
        raise HTTPException(status_code=403, detail="User %d does not own loan %d" % (owner_id, loan_id) )

    return {"success"} if loan_access.add_user(db=db, loan_id=loan_id, user_id=user_id) else {"failure"}

# Run the API
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)