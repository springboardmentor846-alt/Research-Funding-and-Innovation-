from pydantic import BaseModel


class FundingCreate(BaseModel):
    title: str
    funding_agency: str
    research_domain: str
    source_type:str
    funding_amount: int
    deadline: str
    eligibility: str
    description: str