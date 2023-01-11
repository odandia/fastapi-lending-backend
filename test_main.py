from fastapi.testclient import TestClient
from sqlalchemy import create_engine, insert, delete
from sqlalchemy.orm import Session, sessionmaker
from database.db import Base
from main import app, get_db
from model.loans import Loan, LoanSchema, LoanSchemaBase
from model.users import User, UserSchema, UserSchemaBase
from model.loan_access import LoanAccess
import pytest

# Configure tests to use a separate test database
def get_test_db_engine():
    return create_engine("sqlite:///database/test.db", connect_args={"check_same_thread": False})

def get_test_db():
    connection = get_test_db_engine().connect()
    return Session(autocommit=False, autoflush=False, bind=connection)

# Override the get_db function in the main app to use the test database
app.dependency_overrides[get_db] = get_test_db
test_client = TestClient(app)

@pytest.fixture(scope="function")
def engine():
    yield get_test_db_engine()

# Refresh the database tables before and after each function
@pytest.fixture(scope="function")
def tables(engine):
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

# Wrap each test in a transaction, so it's easy to rollback
@pytest.fixture(scope="function")
def test_db(engine, tables):
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

USER_ONE_BASE = UserSchemaBase(username="osman")
USER_ONE_RESPONSE = UserSchema(id=1, **USER_ONE_BASE.dict())
USER_TWO_BASE = UserSchemaBase(username="zac")
USER_TWO_RESPONSE = UserSchema(id=2, **USER_TWO_BASE.dict())

@pytest.fixture()
def setup_users(test_db):
    test_db.add(User(**USER_ONE_BASE.dict()))
    test_db.add(User(**USER_TWO_BASE.dict()))
    test_db.commit()
    yield

LOAN_ONE_BASE = LoanSchemaBase(amount=1000, term=12, apr=0.1, status="active", owner_id=1)
LOAN_ONE_RESPONSE = LoanSchema(id=1, **LOAN_ONE_BASE.dict())
LOAN_TWO_BASE = LoanSchemaBase(amount=1000, term=24, apr=0.2, status="active", owner_id=2)
LOAN_TWO_RESPONSE = LoanSchema(id=1, **LOAN_ONE_BASE.dict())

# Create two loans, and give one to each user
@pytest.fixture()
def setup_loans(test_db, setup_users):
    test_db.add(Loan(**LOAN_ONE_BASE.dict()))
    test_db.add(Loan(**LOAN_TWO_BASE.dict()))
    test_db.add(LoanAccess(user_id=1, loan_id=1))
    test_db.add(LoanAccess(user_id=2, loan_id=2))
    test_db.commit()
    yield

# Share Loan 2 with User 1
@pytest.fixture()
def setup_loan_share(test_db, setup_loans):
    test_db.add(LoanAccess(user_id=2, loan_id=1))
    test_db.commit()
    yield


# Everything above is setup, tests start here:

# Users
def test_create_user(test_db):
    response = test_client.post("/users", json=USER_ONE_BASE.dict())
    assert response.status_code == 200
    assert response.json() == USER_ONE_RESPONSE.dict()

def test_create_invalid_user(test_db):
    response = test_client.post("/users", json={"username": "Ty"})
    assert response.status_code == 400
    assert response.json() == {'detail': "Username must be at least 3 characters"}

def test_list_some_users(setup_users):
    response = test_client.get("/users")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0] == USER_ONE_RESPONSE.dict()
    assert response.json()[1] == USER_TWO_RESPONSE.dict()

def test_list_empty_users(test_db):
    response = test_client.get("/users")
    assert response.status_code == 200
    assert len(response.json()) == 0


# Loans
def test_create_loan(setup_users):
    response = test_client.post("/loans", json=LOAN_ONE_BASE.dict())
    assert response.status_code == 200
    assert response.json() == LOAN_ONE_RESPONSE.dict()

def test_create_loan_for_nonexistent_user(test_db):
    response = test_client.post("/loans", json=LOAN_ONE_BASE.dict())
    assert response.status_code == 404
    assert response.json() == {"detail": "User 1 not found"}

def test_create_loan_with_invalid_amount(setup_users):
    response = test_client.post("/loans", json={"amount": -1, "term": 12, "apr": 0.1, "status": "active", "owner_id": 1})
    assert response.status_code == 400
    assert response.json() == {'detail': 'Loan amount must be greater than zero'}

def test_list_user_loans(setup_loans):
    response = test_client.get("/users/1/loans")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0] == LOAN_ONE_RESPONSE.dict()

def test_update_loan(setup_loans):
    response = test_client.put("/loans/1",
        json={"amount": 1000, "term": 12, "apr": 0.1, "status": "inactive", "owner_id": 1},
        params = {"user_id": 1})

    assert response.status_code == 200
    assert response.json()["status"] == "inactive"

# Sharing only allows viewing, not updates
def test_update_shared_loan(setup_loan_share):
    response = test_client.put("/loans/2",
        json={"amount": 1000, "term": 12, "apr": 0.1, "status": "inactive", "owner_id": 2},
        params = {"user_id": 1})

    assert response.status_code == 403


# Loan Sharing
def test_share_loan(setup_loans):
    response = test_client.get("/users/2/loans")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = test_client.post("/loans/1/share", params={"owner_id": 1, "user_id": 2})
    assert response.status_code == 200
    assert response.json() == ["success"]

    response = test_client.get("/users/2/loans")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_view_shared_loans(setup_loan_share):
    response = test_client.get("/users/2/loans")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_view_unshared_loan(setup_loans):
    response = test_client.get("/loans/1", params={"user_id": 2})
    assert response.status_code == 403


# Calculations -- these need better tests, probably in a test_loans.py
def test_view_loan_schedule(setup_loans):
    response = test_client.get("/loans/1", params={"user_id": 1})
    assert response.status_code == 200
    assert len(response.json()) == LOAN_ONE_BASE.term

def test_view_loan_schedule_without_auth(setup_loans):
    response = test_client.get("/loans/1", params={"user_id": 2})
    assert response.status_code == 403

def test_view_loan_summary(setup_loans):
    response = test_client.get("/loans/1/month/0", params={"user_id": 1})
    assert response.status_code == 200
    assert response.json() == {
        "current_principal": LOAN_ONE_BASE.amount,
        "aggregate_principal_paid": 0.0,
        "aggregate_interest_paid": 0.0
    }
