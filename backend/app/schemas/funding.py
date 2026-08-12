"""
Funding Opportunity Pydantic Schemas
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class FundingOpportunityBase(BaseModel):
    title: str
    agency: str
    opportunity_type: str
    description: str
    total_funding_amount: float = 0.0
    min_award: float = 0.0
    max_award: float = 0.0
    currency: str = "USD"
    deadline: Optional[datetime] = None
    application_url: Optional[str] = None
    status: str = "OPEN"
    eligibility_criteria: List[str] = []
    target_domains: List[str] = []
    target_keywords: List[str] = []
    eligible_applicant_types: List[str] = []


class FundingOpportunityCreate(FundingOpportunityBase):
    pass


class FundingOpportunityResponse(FundingOpportunityBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    match_score: Optional[float] = None # Dynamically injected for user queries


class GrantEligibilityRequest(BaseModel):
    research_domains: List[str] = []
    keywords: List[str] = []
    organization_type: str = "Researcher"


class GrantEligibilityResponse(BaseModel):
    grant_id: str
    grant_title: str
    agency: str
    match_score: float
    matched_domains: List[str]
    matched_keywords: List[str]
    eligibility_status: str # High Match, Medium Match, Low Match
    recommendations: List[str]


class SavedGrantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    grant_id: str
    match_score: float
    status: str
    notes: Optional[str] = None
    grant: Optional[FundingOpportunityResponse] = None
