"""
Pydantic schemas for Research Intelligence Papers, Trends, Search, and AI Recommendations.
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


# ── Paper Schemas ─────────────────────────────────────────────────────────────
class ResearchPaperBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=512)
    abstract: str = Field(..., min_length=10)
    authors: List[str] = Field(default_factory=list)
    venue: str = Field(..., min_length=2, max_length=255)
    publication_year: int = Field(..., ge=1900, le=2100)
    doi: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = Field(None, max_length=512)
    citations_count: int = Field(0, ge=0)
    influential_citations_count: int = Field(0, ge=0)
    research_domains: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    open_access: bool = True
    source_api: str = Field("local_seed", max_length=100)
    external_id: Optional[str] = Field(None, max_length=255)


class ResearchPaperCreate(ResearchPaperBase):
    pass


class ResearchPaperResponse(ResearchPaperBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResearchPaperListResponse(BaseModel):
    items: List[ResearchPaperResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ── Trend Schemas ──────────────────────────────────────────────────────────────
class ResearchTrendResponse(BaseModel):
    id: uuid.UUID
    topic_name: str
    research_domain: str
    growth_rate: float
    paper_count: int
    key_keywords: List[str]
    is_emerging: bool
    summary: str
    year: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResearchTrendListResponse(BaseModel):
    items: List[ResearchTrendResponse]
    total: int


# ── AI Recommendation Schema ──────────────────────────────────────────────────
class PaperRecommendationResponse(BaseModel):
    paper: ResearchPaperResponse
    match_score: float = Field(..., ge=0.0, le=100.0)
    matching_reason: str
    matched_keywords: List[str] = Field(default_factory=list)
    matched_domains: List[str] = Field(default_factory=list)


# ── Dashboard Summary Schema ──────────────────────────────────────────────────
class ResearchIntelligenceDashboardSummaryResponse(BaseModel):
    recommended_papers: List[PaperRecommendationResponse]
    trending_topics: List[ResearchTrendResponse]
    emerging_topics: List[ResearchTrendResponse]
    recent_publications: List[ResearchPaperResponse]
    statistics: Dict[str, Any]
