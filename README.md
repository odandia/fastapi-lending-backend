# Osman Dandia / Lending App

## Setup

Prereqs:
```
 * python3.11 (fastapi requires 3.7+)
 * python3.11-distutils (required by python3.11, I had to install it separately on ubuntu)
 * pip3
 * virtualenv
```

Install Dependencies:
```
 $ cd <repo>
 $ virtualenv -p python3.11 venv
 $ source venv/bin/activate
 $ pip install -r requirements.txt
```

## Run Server:  
```
 $ python3 main.py
```
 
 
## Run Tests:
```
 $ pytest 
```

## Notes
* Loading the index at `localhost:8000` will redirect to `localhost:8000/docs`, where you can view the OpenAPI spec and use the interface to test calls to the API. 
  * The OpenAPI Spec can also be imported into a tool like Postman for API testing. 
* Loan schedule math comes out off by a fraction (slightly over or underpays by end of term), not entirely sure why. Amortization math was ripped from investopedia, could use a review from someone more versed in lending. 
* Doing user authorization without authentication (for loan sharing) is kinda wonky. Consider the provided `user_id` param to represent an authenticated user, and it all makes sense. 
    * Updates require ownership
    * Reads require ownership or sharing
 
### Requirements

 * ./ Create a User
 * ./ Create a Loan
 * ./ Fetch all Loans for a User
     * ./ Amount
     * ./ Annual Interest Rate
     * ./ Loan Term in months
 * ./ Share Loan with another User
 * ./ Fetch Loan Schedule
 * ./ Fetch Loan Summary for specific month

Optional:
 * ./ Use pytests or other test framework to test your endpoints and
financial calculations
 * ./ Use an ORM + SQL DB to save users and loans. We’d recommend using
SQLAlchemy or SQLModel, with an in-memory instance of SQLite -
but that is up to you.

We’ll be scoring you based on,
 * Proper HTTP methods
 * Error handling and validation
 * API structuring
 * Calculation Accuracy
 * Git commits
