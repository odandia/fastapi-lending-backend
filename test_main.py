from fastapi.testclient import TestClient
from main import app
from model import Loan
import pytest

# @pytest.fixture(autouse=True)
# def run_around_tests():
#     # Runs before each test
#     loans = {}
#     yield
#     # Runs after each test
#     loans = {}

LOAN_ONE = Loan(id=1, amount=1000, term=12, interest_rate=0.1, status="active")
LOAN_TWO = Loan(id=2, amount=1000, term=24, interest_rate=0.08, status="active")

MULTIPLE_LOANS = {
    1: LOAN_ONE,
    2: LOAN_TWO
}

@pytest.fixture
def no_loans():
    app.state.loans = {}
    return app.state.loans

@pytest.fixture
def single_loan():
    app.state.loans = {1: LOAN_ONE}
    return app.state.loans

@pytest.fixture
def multiple_loans():
    app.state.loans = MULTIPLE_LOANS
    return app.state.loans

@pytest.fixture(autouse=True)
def test_client():
    return TestClient(app)

# Creates
def test_create_loan(test_client, no_loans):
    response = test_client.post("/loans", json=LOAN_ONE.to_json())
    assert response.status_code == 200
    assert response.json() == LOAN_ONE.to_json()

def test_create_existing_loan(test_client, single_loan):
    response = test_client.post("/loans", json=LOAN_ONE.to_json())
    assert response.status_code == 400
    assert response.json() == {"detail": "Loan 1 already exists"}

def test_create_loan_with_invalid_amount(test_client, no_loans):
    response = test_client.post("/loans", json={"id": 1, "amount": -1, "term": 12, "interest_rate": 0.1, "status": "active"})
    assert response.status_code == 400
    assert response.json() == {'detail': 'Loan amount must be greater than zero'}

# Reads
def test_read_loans(test_client, multiple_loans):
    response = test_client.get("/loans")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json() == list(multiple_loans.values())

def test_read_empty_loans(test_client, no_loans):
    response = test_client.get("/loans")
    assert response.status_code == 200
    assert response.json() == []

def test_read_loan(test_client, single_loan):
    response = test_client.get("/loans")
    assert response.status_code == 200
    assert response.json() == [LOAN_ONE.to_json()]

def test_read_nonexistent_loan(test_client, no_loans):
    response = test_client.get("/loans/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Loan 1 not found"}

# Updates
def test_update_loan(test_client, single_loan):
    new_loan = {"id": 1, "amount": 2000, "term": 24, "interest_rate": 0.2, "status": "active"}
    response = test_client.put("/loans/1", json=new_loan)
    assert response.status_code == 200
    assert response.json() == new_loan

def test_update_nonexistent_loan(test_client, no_loans):
    response = test_client.put("/loans/1", json=LOAN_ONE.to_json())
    assert response.status_code == 404
    assert response.json() == {"detail": "Loan 1 not found"}

# Deletes
def test_delete_loan(test_client, single_loan):
    response = test_client.delete("/loans/1")
    assert response.status_code == 200
    assert response.json() == {"success": True}
    assert test_client.get("/loans").json() == []

def test_delete_nonexistent_loan(test_client, no_loans):
    response = test_client.delete("/loans/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Loan 1 not found"}

# Interest Calculation
def test_calculate_interest(test_client, single_loan):
    response = test_client.get("/loans/1/interest")
    assert response.status_code == 200
    assert response.json() == {"interest": 1200.0}

def test_calculate_interest_nonexistent_loan(test_client, no_loans):
    response = test_client.get("/loans/1/interest")
    assert response.status_code == 404
    assert response.json() == {"detail": "Loan 1 not found"}