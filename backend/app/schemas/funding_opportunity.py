from datetime import date
from pydantic import BaseModel


class FundingOpportunityCreate(BaseModel):
    title: str
    organization: str
    description: str
    eligibility: str
    funding_amount: str
    deadline: date
    research_domain: str


class FundingOpportunityResponse(BaseModel):
    id: int
    title: str
    organization: str
    description: str
    eligibility: str
    funding_amount: str
    deadline: date
    research_domain: str

    class Config:
        from_attributes = True