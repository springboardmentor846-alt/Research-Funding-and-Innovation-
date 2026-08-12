"""
Research Publication & Trend Intelligence Pydantic Schemas
"""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict


class PublicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    authors: List[str] = []
    journal_or_venue: Optional[str] = None
    publication_year: int
    publication_date: Optional[datetime] = None
    abstract: Optional[str] = None
    citation_count: int = 0
    doi: Optional[str] = None
    paper_url: Optional[str] = None
    domains: List[str] = []
    keywords: List[str] = []
    source_database: str = "OpenAlex"


class ResearchTrendResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    topic_name: str
    domain: str
    growth_rate_pct: float
    publication_count: int
    citation_velocity: float
    hotspot_score: float
    maturity_stage: str
    yearly_volume_series: Dict[str, int] = {}
    key_keywords: List[str] = []


class ResearchIntelligenceOverview(BaseModel):
    total_publications_indexed: int
    active_research_topics: int
    emerging_hotspots: int
    top_domains: List[str]
    emerging_trends: List[ResearchTrendResponse]
    recent_publications: List[PublicationResponse]
