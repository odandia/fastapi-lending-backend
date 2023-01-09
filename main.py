import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
# from model.loan import Loan
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from database.db import SessionLocal, engine, Base
from model import user, loan

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users", response_model=user.UserSchema)
def create_user(userData: user.UserSchemaBase, db: Session = Depends(get_db)):
    return user.create_user(db=db, userData=userData)


@app.get("/users", response_model=List[user.UserSchema])
def list_users(db: Session = Depends(get_db)):
    return user.get_users(db=db)


# # map of ID to Loan
# app.state.loans = {}

# # redirect / to /docs
# @app.get("/", response_class=RedirectResponse)
# async def redirect_to_docs():
#     return "/docs"

# # route to create a new loan
# @app.post("/loans", response_model=Loan)
# async def create_loan(loan: Loan):
#     err = validate_loan(loan)
#     if err:
#         raise err
#     app.state.loans[loan.id] = loan
#     return loan

# def validate_loan(loan: Loan):
#     print(loan)
#     if loan.id in app.state.loans:
#         return HTTPException(status_code=400, detail="Loan %d already exists" % loan.id )
#     if not isinstance(loan.amount, float):
#         return HTTPException(status_code=400, detail="Loan amount must be a float" )
#     if loan.amount <= 0:
#         return HTTPException(status_code=400, detail="Loan amount must be greater than zero" )
#     if not isinstance(loan.interest_rate, float):
#         return HTTPException(status_code=400, detail="Loan interest_rate must be a float" )
#     if not isinstance(loan.term, int):
#         return HTTPException(status_code=400, detail="Loan term must be an int" )
#     if not isinstance(loan.status, str):
#         return HTTPException(status_code=400, detail="Loan status must be a string" )
#     if loan.status not in ["active", "inactive"]:
#         return HTTPException(status_code=400, detail="Loan status must be either 'active' or 'inactive'" )
#     else:
#         return None

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