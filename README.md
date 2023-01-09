*Greystone / Osman Dandia*

**Setup**

Prereqs:
 * python3
 * pip
 * virtualenv

Install Dependencies:
 * virtualenv -p python3 venv
 * source venv/bin/activate
 * pip install -r requirements.txt

Run Server:
 * python3 main.py
 
Loading the index at `localhost:8000` will redirect to `localhost:8000/docs`, where you can view the OpenAPI spec and use the interface to test calls to the API. 
 
Run Tests:
 * pytest 