"""
Research Publications & Trend Intelligence Models Definition
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Publication(Base):
    """
    Academic publication entry harvested from OpenAlex, CrossRef, Semantic Scholar, etc.
    """
    __tablename__ = "publications"

    title: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    authors: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    journal_or_venue: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    publication_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    publication_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    citation_count: Mapped[int] = mapped_column(Integer, default=0, index=True)
    doi: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    paper_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    
    domains: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    keywords: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    source_database: Mapped[str] = mapped_column(String(100), default="OpenAlex") # OpenAlex, CrossRef, Semantic Scholar

    def __repr__(self) -> str:
        return f"<Publication(id={self.id}, title='{self.title[:30]}...', year={self.publication_year})>"


class ResearchTrend(Base):
    """
    Analyzed topic trend metrics for Emerging Topic Detection and Hotspot Tracking.
    """
    __tablename__ = "research_trends"

    topic_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    growth_rate_pct: Mapped[float] = mapped_column(Float, default=0.0) # Annual growth velocity %
    publication_count: Mapped[int] = mapped_column(Integer, default=0)
    citation_velocity: Mapped[float] = mapped_column(Float, default=0.0) # Citations/year rate
    hotspot_score: Mapped[float] = mapped_column(Float, default=0.0) # 0-100 Hotspot metric
    maturity_stage: Mapped[str] = mapped_column(String(50), default="Emerging") # Emerging, Growing, Mature, Declining

    # Historical time series metric data points stored in JSON
    yearly_volume_series: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    key_keywords: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    def __repr__(self) -> str:
        return f"<ResearchTrend(topic='{self.topic_name}', growth={self.growth_rate_pct}%, score={self.hotspot_score})>"
