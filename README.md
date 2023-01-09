***Greystone / Osman Dandia***

**Setup**

Prereqs:
 * python3
 * pip
 * virtualenv

Install Dependencies:
```
 $ cd greystone-osman
 $ virtualenv -p python3 venv
 $ source venv/bin/activate
 $ pip install -r requirements.txt
```

Run Server:  
```
 $ python3 main.py
```
 
Loading the index at `localhost:8000` will redirect to `localhost:8000/docs`, where you can view the OpenAPI spec and use the interface to test calls to the API. 
 
Run Tests:
```
 $ pytest 
```
 
 
**Requirements** 
* Create a User
* Create Loan
* Fetch all Loans for a User
    * Amount
    * Annual Interest Rate
    * Loan Term in months
* Share Loan with another User
* Fetch Loan Schedule
    {
        Month: n
        Remaining balance: $xxxx,
        Monthly payment: $xxx
    }
* Fetch Loan Summary for specific month
    * Current principal balance at given month
    * The aggregate amount of principal already paid
    * The aggregate amount of interest already paid
