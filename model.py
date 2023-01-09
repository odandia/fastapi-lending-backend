from pydantic import BaseModel

# Define a loan model using pydantic
class Loan(BaseModel):
    id: int
    amount: float
    term: int
    interest_rate: float
    status: str

    def __init__(self, id, amount,term, interest_rate, status):
        super().__init__(id=id, amount=amount, term=term, interest_rate=interest_rate, status=status)

    def to_json(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "term": self.term,
            "interest_rate": self.interest_rate,
            "status": self.status,
        }

    def calculate_interest(self):
        return self.amount * self.interest_rate * self.term
