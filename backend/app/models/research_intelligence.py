"""
SQLAlchemy models for Research Papers, Citations, and Research Trends.
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class ResearchPaper(Base):
    """Scientific research paper metadata item."""

    __tablename__ = "research_papers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    abstract: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    venue: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    publication_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    doi: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    
    citations_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    influential_citations_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    research_domains: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    keywords: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    open_access: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Provider abstraction field for OpenAlex, Semantic Scholar, CrossRef, etc.
    source_api: Mapped[str] = mapped_column(String(100), default="local_seed", nullable=False)
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ResearchPaper id={self.id} title={self.title[:30]} year={self.publication_year}>"


class ResearchTrend(Base):
    """Trending and emerging research topics intelligence."""

    __tablename__ = "research_trends"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    topic_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    research_domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    growth_rate: Mapped[float] = mapped_column(Float, nullable=False)  # e.g., 42.5 for +42.5%
    paper_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    key_keywords: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    is_emerging: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    year: Mapped[int] = mapped_column(Integer, default=2024, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ResearchTrend id={self.id} topic={self.topic_name} growth={self.growth_rate}%>"
