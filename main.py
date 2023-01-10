import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
# from model.loan import Loan
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from database.db import SessionLocal, engine, Base
from model import loans, users

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# redirect / to /docs
@app.get("/", response_class=RedirectResponse)
async def redirect_to_docs():
    return "/docs"

@app.post("/users", response_model=users.UserSchema)
def create_user(userData: users.UserSchemaBase, db: Session = Depends(get_db)):
    return users.create_user(db=db, userData=userData)

@app.get("/users", response_model=List[users.UserSchema])
def list_users(db: Session = Depends(get_db)):
    return users.get_users(db=db)

# route to create a new loan
@app.post("/loans", response_model=loans.LoanSchema)
def create_loan(loanData: loans.LoanSchemaBase, db: Session = Depends(get_db)):
    err = loans.validateLoan(loanData)
    if err:
        raise err

    owner = users.get_user_by_id(db=db, id=loanData.owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="User %d not found" % loanData.owner_id )

    return loans.create_loan(db=db, loanData=loanData)

@app.get("/users/{user_id}/loans", response_model=List[loans.LoanSchema])
def list_user_loans(user_id: int, db: Session = Depends(get_db)):
    return loans.get_loans_by_owner_id(db=db, owner_id=user_id)

# # route to get a list of all loans
# @app.get("/loans", response_model=List[Loan])
# async def read_loans():
#     return list(app.state.loans.values())

# # route to get a loan by id
# @app.get("/loans/{id}", response_model=Loan)
# async def read_loan(id: int):
#     if id not in app.state.loans:
#         raise HTTPException(status_code=404, detail="Loan %d not found" % id )
#     return app.state.loans[id]

# # route to update a loan by id
# @app.put("/loans/{id}", response_model=Loan)
# async def update_loan(id: int, loan: Loan):
#     if id not in app.state.loans:
#         raise HTTPException(status_code=404, detail="Loan %d not found" % id )
#     app.state.loans.pop(id)
#     app.state.loans[loan.id] = loan
#     return loan

# # route to delete a loan by id
# @app.delete("/loans/{id}")
# async def delete_loan(id: int) -> JSONResponse:
#     if id not in app.state.loans:
#         raise HTTPException(status_code=404, detail="Loan %d not found" % id )
#     app.state.loans.pop(id)
#     return JSONResponse(content={"success": True})

# # route to compute the interest for a given loan
# @app.get("/loans/{id}/interest")
# async def calculate_interest(id: int) -> JSONResponse:
#     if id not in app.state.loans:
#         raise HTTPException(status_code=404, detail="Loan %d not found" % id )
#     interest = app.state.loans[id].calculate_interest()
#     return JSONResponse(content={"interest": interest})

# Run the API
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)