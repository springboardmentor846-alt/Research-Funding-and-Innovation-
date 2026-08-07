"""
Pydantic schemas for Technology Intelligence & Innovation Scoring.
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class TechnologyTrendBase(BaseModel):
    name: str
    technology_domain: str
    trl_level: int = Field(..., ge=1, le=9)
    maturity_level: str
    growth_rate: float
    market_size_usd_b: float
    key_players: List[str] = Field(default_factory=list)
    key_keywords: List[str] = Field(default_factory=list)
    is_emerging: bool = True
    summary: str
    opportunity_description: str
    year: int = 2025


class TechnologyTrendResponse(TechnologyTrendBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TechnologyTrendListResponse(BaseModel):
    items: List[TechnologyTrendResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class InnovationScoreBreakdown(BaseModel):
    publications_count: int
    total_citations: int
    h_index: int
    patents_count: int
    granted_patents_count: int
    domains_matched: List[str]
    technology_interests: List[str]
    strengths: List[str]
    growth_areas: List[str]


class InnovationScoreResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    overall_score: float = Field(..., description="Overall Innovation Index (0-100)")
    trl_level: int = Field(..., ge=1, le=9, description="Calculated Technology Readiness Level")
    research_strength: float = Field(..., description="Scientific research capacity score (0-100)")
    patent_strength: float = Field(..., description="IP protection & commercialization score (0-100)")
    commercial_potential: float = Field(..., description="Market viability score (0-100)")
    recommendation_summary: str = Field(..., description="AI strategic advice and next steps")
    breakdown_details: InnovationScoreBreakdown
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OpportunityAnalysisItem(BaseModel):
    id: uuid.UUID
    title: str
    technology_domain: str
    market_size_usd_b: float
    growth_rate: float
    maturity_level: str
    opportunity_gap: str
    alignment_score: float
    recommended_action: str
    key_keywords: List[str]


class OpportunityAnalysisResponse(BaseModel):
    total_opportunities: int
    high_alignment_count: int
    top_domains: List[str]
    opportunities: List[OpportunityAnalysisItem]


class TechnologyStatisticsSummary(BaseModel):
    total_trends_indexed: int
    emerging_count: int
    avg_growth_rate: float
    top_tech_domain: str


class TechnologyDashboardSummaryResponse(BaseModel):
    statistics: TechnologyStatisticsSummary
    emerging_technologies: List[TechnologyTrendResponse]
    innovation_score: Optional[InnovationScoreResponse] = None
    recommended_opportunities: List[OpportunityAnalysisItem]
