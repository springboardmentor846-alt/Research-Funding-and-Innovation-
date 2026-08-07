"""
Pydantic schemas for Commercialization & Industry Collaboration.
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, EmailStr


class CommercializationOpportunityBase(BaseModel):
    title: str
    organization_name: str
    industry: str
    technology_domain: str
    opportunity_type: str = "Technology Licensing"  # Technology Licensing, Joint R&D, Corporate Venture Capital, Startup Accelerator, Contract Research
    summary: str
    detailed_description: str
    trl_requirement: int = Field(4, ge=1, le=9)
    estimated_funding_usd: Optional[float] = None
    contact_email: str
    contact_person: str
    location: str
    key_keywords: List[str] = Field(default_factory=list)
    matching_technologies: List[str] = Field(default_factory=list)
    deadline: Optional[str] = None
    is_active: bool = True


class CommercializationOpportunityCreate(CommercializationOpportunityBase):
    pass


class CommercializationOpportunityUpdate(BaseModel):
    title: Optional[str] = None
    organization_name: Optional[str] = None
    industry: Optional[str] = None
    technology_domain: Optional[str] = None
    opportunity_type: Optional[str] = None
    summary: Optional[str] = None
    detailed_description: Optional[str] = None
    trl_requirement: Optional[int] = None
    estimated_funding_usd: Optional[float] = None
    contact_email: Optional[str] = None
    contact_person: Optional[str] = None
    location: Optional[str] = None
    key_keywords: Optional[List[str]] = None
    matching_technologies: Optional[List[str]] = None
    deadline: Optional[str] = None
    is_active: Optional[bool] = None


class CommercializationOpportunityResponse(CommercializationOpportunityBase):
    id: uuid.UUID
    is_bookmarked: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommercializationOpportunityListResponse(BaseModel):
    items: List[CommercializationOpportunityResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class IndustryPartnerResponse(BaseModel):
    id: uuid.UUID
    name: str
    industry: str
    organization_type: str
    technology_focus: List[str]
    description: str
    website_url: Optional[str] = None
    contact_email: str
    location: str
    collaboration_types: List[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StartupRecommendationResponse(BaseModel):
    id: uuid.UUID
    program_name: str
    organizer: str
    program_type: str
    technology_domain: str
    funding_amount_usd: float
    equity_taken_pct: float
    duration_months: int
    description: str
    eligibility_criteria: str
    website_url: Optional[str] = None
    deadline: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommercializationRecommendationResponse(CommercializationOpportunityResponse):
    match_score: float = Field(..., description="Match percentage score from 0 to 100")
    matching_technologies: List[str] = Field(default_factory=list)
    recommendation_reason: str = Field(...)
    suggested_industry_partner: str = Field(...)


class CollaborationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    opportunity_id: uuid.UUID
    status: str
    message: Optional[str] = None
    opportunity: Optional[CommercializationOpportunityResponse] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CollaborationRequestCreate(BaseModel):
    status: str = "contacted"  # bookmarked, contacted, under_review
    message: Optional[str] = None


class CommercializationStatisticsSummary(BaseModel):
    total_opportunities: int
    active_partners: int
    startup_programs_count: int
    collaboration_requests: int
    top_industry: str


class CommercializationDashboardSummaryResponse(BaseModel):
    statistics: CommercializationStatisticsSummary
    recommended_opportunities: List[CommercializationRecommendationResponse]
    industry_partners: List[IndustryPartnerResponse]
    startup_programs: List[StartupRecommendationResponse]
    collaboration_requests: List[CollaborationResponse]
