"""Pydantic v2 schemas for the patent analytics module.

These are the request/response shapes used by the public API and the
internal service layer.  They mirror the style of ``schemas/publication.py``.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Base / Create / Update
# ---------------------------------------------------------------------------


class PatentBase(BaseModel):
    patent_number: str = Field(..., min_length=1, max_length=64)
    title: str = Field(..., min_length=1, max_length=1024)
    abstract: Optional[str] = None
    inventors: Optional[str] = None
    assignee: Optional[str] = None
    technology_area: Optional[str] = None
    keywords: Optional[str] = None
    country: Optional[str] = None
    classification: Optional[str] = None
    classification_label: Optional[str] = None
    filing_date: Optional[datetime] = None
    publication_date: Optional[datetime] = None
    publication_year: Optional[int] = None
    citations: int = 0
    patent_family: Optional[str] = None
    legal_status: Optional[str] = None
    source: str = Field(..., min_length=1, max_length=32)
    source_id: Optional[str] = None
    url: Optional[str] = None


class PatentCreate(PatentBase):
    extra_metadata: Optional[Dict[str, Any]] = None


class PatentUpdate(BaseModel):
    title: Optional[str] = None
    abstract: Optional[str] = None
    inventors: Optional[str] = None
    assignee: Optional[str] = None
    technology_area: Optional[str] = None
    keywords: Optional[str] = None
    country: Optional[str] = None
    classification: Optional[str] = None
    classification_label: Optional[str] = None
    filing_date: Optional[datetime] = None
    publication_date: Optional[datetime] = None
    publication_year: Optional[int] = None
    citations: Optional[int] = None
    patent_family: Optional[str] = None
    legal_status: Optional[str] = None
    url: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class PatentResponse(PatentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
    cluster_id: Optional[int] = None


class PatentListResponse(BaseModel):
    """Paginated patent list, returned by /patents/search and /patents/analytics listings."""

    items: List[PatentResponse]
    total: int
    page: int = 1
    page_size: int = 20
    sources: Optional[List[str]] = None
    query: Optional[str] = None


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------


class SourceCount(BaseModel):
    source: str
    count: int


class TechnologyCount(BaseModel):
    technology: str
    count: int


class CountryCount(BaseModel):
    country: str
    count: int


class YearCount(BaseModel):
    year: int
    count: int
    citations: int = 0


class AssigneeCount(BaseModel):
    assignee: str
    count: int
    total_citations: int = 0


class InventorCount(BaseModel):
    inventor: str
    count: int


class CitationStats(BaseModel):
    total: int
    average: float
    max: int
    highly_cited_count: int   # citations >= 10


class GrowthPoint(BaseModel):
    year: int
    count: int
    growth_rate: Optional[float] = None


class PatentAnalyticsOverview(BaseModel):
    """Top-level analytics payload consumed by the existing React UI."""

    total_patents: int
    total_citations: int
    by_source: List[SourceCount]
    by_technology: List[TechnologyCount]
    by_year: List[YearCount] = []
    by_country: List[CountryCount] = []
    top_assignees: List[AssigneeCount] = []
    top_inventors: List[InventorCount] = []
    citation_stats: CitationStats
    growth_trend: List[GrowthPoint] = []
    most_active_organizations: List[AssigneeCount] = []


# ---------------------------------------------------------------------------
# Technology Intelligence
# ---------------------------------------------------------------------------


class TechnologyTrendPoint(BaseModel):
    technology_area: str
    publication_year: int
    patent_count: int
    total_citations: int
    growth_rate: Optional[float] = None
    is_emerging: bool = False
    is_fast_growing: bool = False


class TechnologyCluster(BaseModel):
    cluster_id: int
    label: Optional[str] = None
    size: int
    keywords: List[str] = []


class SimilarPatent(BaseModel):
    patent_id: int
    patent_number: str
    title: str
    similarity: float
    reason: str


class TechnologyIntelligenceReport(BaseModel):
    emerging_technologies: List[TechnologyTrendPoint]
    fast_growing_technologies: List[TechnologyTrendPoint]
    highly_cited_patents: List[PatentResponse]
    clusters: List[TechnologyCluster]
    similar_patents: List[SimilarPatent] = []


# ---------------------------------------------------------------------------
# Innovation scoring
# ---------------------------------------------------------------------------


class InnovationScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    patent_id: int
    novelty_score: float
    technology_growth_score: float
    citation_impact_score: float
    patent_density_score: float
    recent_activity_score: float
    final_score: float
    explanation: Optional[Dict[str, Any]] = None
    computed_at: datetime


# ---------------------------------------------------------------------------
# Commercialization
# ---------------------------------------------------------------------------


class CommercializationRecommendation(BaseModel):
    patent_id: int
    label: str  # High Commercial Potential | Consider Patent Filing | Highly Competitive Technology | Emerging Technology | Strong Licensing Opportunity
    reason: str
    innovation_score: float
    technology_growth: float
    patent_activity: int
    competition_level: str
    citation_trend: float
    computed_at: datetime


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


class DashboardResponse(BaseModel):
    generated_at: datetime
    total_patents: int
    total_citations: int
    innovation_score_avg: float
    commercialization_summary: Dict[str, int]
    analytics: PatentAnalyticsOverview
    technology_intelligence: TechnologyIntelligenceReport
    recommendations: List[CommercializationRecommendation] = []


# ---------------------------------------------------------------------------
# AI Explainer
# ---------------------------------------------------------------------------


class PatentExplainRequest(BaseModel):
    patent_text: str = Field(..., min_length=100)


class PatentExplainResponse(BaseModel):
    explanation: str
