"""
Pydantic schemas for Patent Intelligence API requests and responses.
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class PatentRecordBase(BaseModel):
    patent_number: str
    title: str
    abstract: str
    assignee_organization: str
    inventors: List[str] = Field(default_factory=list)
    technology_domain: str
    ipc_codes: List[str] = Field(default_factory=list)
    cpc_codes: List[str] = Field(default_factory=list)
    filing_date: str
    publication_date: str
    publication_year: int
    status: str = "Granted"  # Granted, Pending, Expired, Abandoned
    claims_count: int = 1
    citations_count: int = 0
    url: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    source_api: str = "local_seed"
    external_id: Optional[str] = None


class PatentRecordResponse(PatentRecordBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PatentRecordListResponse(BaseModel):
    items: List[PatentRecordResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PatentTrendResponse(BaseModel):
    id: uuid.UUID
    technology_domain: str
    growth_rate: float
    patent_count: int
    top_assignees: List[str]
    key_keywords: List[str]
    is_emerging: bool
    summary: str
    year: int

    model_config = ConfigDict(from_attributes=True)


class PatentRecommendationResponse(PatentRecordResponse):
    match_score: float = Field(..., description="Match percentage score from 0 to 100")
    matching_fields: List[str] = Field(default_factory=list, description="Fields matched: Research Domains, Technology Interests, Keywords")
    recommendation_reason: str = Field(..., description="Human-readable explanation of the AI match")


class PatentOrganizationStat(BaseModel):
    name: str
    count: int
    percentage: float


class PatentDomainStat(BaseModel):
    domain: str
    count: int
    percentage: float


class PatentYearStat(BaseModel):
    year: int
    count: int


class PatentStatusStat(BaseModel):
    status: str
    count: int


class PatentAnalyticsResponse(BaseModel):
    total_patents: int
    granted_patents: int
    pending_patents: int
    expired_patents: int
    top_organizations: List[PatentOrganizationStat]
    technology_domains: List[PatentDomainStat]
    publication_years: List[PatentYearStat]
    status_distribution: List[PatentStatusStat]


class PatentStatisticsSummary(BaseModel):
    total_patents_indexed: int
    granted_count: int
    pending_count: int
    top_domain: str


class PatentDashboardSummaryResponse(BaseModel):
    statistics: PatentStatisticsSummary
    recent_patents: List[PatentRecordResponse]
    top_organizations: List[PatentOrganizationStat]
    trending_technologies: List[PatentTrendResponse]
    recommendations: List[PatentRecommendationResponse]
