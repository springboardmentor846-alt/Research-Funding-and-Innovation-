"""
Pydantic schemas for Funding Opportunities, Bookmarks, Alerts, and Recommendations.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ── Funding Opportunity Schemas ───────────────────────────────────────────────
class FundingOpportunityBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=512)
    funder_name: str = Field(..., min_length=2, max_length=255)
    funder_type: str = Field("Government", max_length=100)
    description: str = Field(..., min_length=10)
    amount_min: Optional[float] = Field(None, ge=0)
    amount_max: Optional[float] = Field(None, ge=0)
    currency: str = Field("USD", max_length=10)
    deadline: Optional[datetime] = None
    funding_type: str = Field("Grant", max_length=100)
    eligible_countries: List[str] = Field(default_factory=list)
    research_domains: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    application_url: str = Field(..., max_length=512)
    is_active: bool = True


class FundingOpportunityCreate(FundingOpportunityBase):
    pass


class FundingOpportunityUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=512)
    funder_name: Optional[str] = Field(None, min_length=2, max_length=255)
    funder_type: Optional[str] = None
    description: Optional[str] = None
    amount_min: Optional[float] = Field(None, ge=0)
    amount_max: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = None
    deadline: Optional[datetime] = None
    funding_type: Optional[str] = None
    eligible_countries: Optional[List[str]] = None
    research_domains: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    application_url: Optional[str] = None
    is_active: Optional[bool] = None


class FundingOpportunityResponse(FundingOpportunityBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_bookmarked: bool = False

    model_config = ConfigDict(from_attributes=True)


class FundingOpportunityListResponse(BaseModel):
    items: List[FundingOpportunityResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ── Bookmark Schemas ──────────────────────────────────────────────────────────
class FundingBookmarkResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    funding_opportunity_id: uuid.UUID
    created_at: datetime
    opportunity: Optional[FundingOpportunityResponse] = None

    model_config = ConfigDict(from_attributes=True)


# ── Alert Schemas ─────────────────────────────────────────────────────────────
class FundingAlertBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    keywords: List[str] = Field(default_factory=list)
    research_domains: List[str] = Field(default_factory=list)
    funding_type: Optional[str] = None
    country: Optional[str] = None
    frequency: str = Field("weekly", max_length=50)
    is_active: bool = True


class FundingAlertCreate(FundingAlertBase):
    pass


class FundingAlertUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    keywords: Optional[List[str]] = None
    research_domains: Optional[List[str]] = None
    funding_type: Optional[str] = None
    country: Optional[str] = None
    frequency: Optional[str] = None
    is_active: Optional[bool] = None


class FundingAlertResponse(FundingAlertBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Recommendation Schema ─────────────────────────────────────────────────────
class FundingRecommendationResponse(BaseModel):
    opportunity: FundingOpportunityResponse
    match_score: float = Field(..., ge=0.0, le=100.0)
    matched_keywords: List[str] = Field(default_factory=list)
    matched_domains: List[str] = Field(default_factory=list)


# ── Dashboard Summary Schema ──────────────────────────────────────────────────
class FundingDashboardSummaryResponse(BaseModel):
    recommended_grants: List[FundingRecommendationResponse]
    latest_grants: List[FundingOpportunityResponse]
    closing_soon_grants: List[FundingOpportunityResponse]
    saved_grants_count: int
    total_opportunities_count: int
