from pydantic import BaseModel
from datetime import date

class FundingOpportunity(BaseModel):
    funding_name: str
    domain: str
    amount: int
    eligibility: str
    deadline: date