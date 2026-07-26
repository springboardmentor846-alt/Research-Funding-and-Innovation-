from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class FundingCreate(BaseModel):
    title: str
    agency: str
    funding_amount: float
    deadline: date
    country: str
    research_domain: str
    eligibility: str
    description: str
    application_link: Optional[str] = None
    status: Optional[str] = "Open"


class FundingResponse(FundingCreate):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FundingFilter(BaseModel):
    research_domain: Optional[str] = None
    country: Optional[str] = None
    agency: Optional[str] = None
    deadline_before: Optional[date] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    sort_by: Optional[str] = "latest"  # latest | highest_amount | deadline
