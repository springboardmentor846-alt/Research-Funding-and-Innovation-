"""
SQLAlchemy models for Patent Intelligence and Patent Trends.
"""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class PatentRecord(Base):
    """Global patent record for search, analytics, and intelligence."""

    __tablename__ = "patent_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patent_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    abstract: Mapped[str] = mapped_column(Text, nullable=False)
    
    assignee_organization: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    inventors: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    technology_domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    ipc_codes: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    cpc_codes: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    filing_date: Mapped[str] = mapped_column(String(50), nullable=False)
    publication_date: Mapped[str] = mapped_column(String(50), nullable=False)
    publication_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    status: Mapped[str] = mapped_column(String(50), default="Granted", nullable=False, index=True)  # Granted, Pending, Expired, Abandoned
    claims_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    citations_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    
    url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    keywords: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    # Provider integration architecture support (Google Patents, USPTO, The Lens)
    source_api: Mapped[str] = mapped_column(String(100), default="local_seed", nullable=False)
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<PatentRecord number={self.patent_number} title={self.title[:30]}>"


class PatentTrend(Base):
    """Trending patent technology domains and emerging innovation intelligence."""

    __tablename__ = "patent_trends"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    technology_domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    growth_rate: Mapped[float] = mapped_column(Float, nullable=False)  # e.g., 38.4 for +38.4%
    patent_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    top_assignees: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    key_keywords: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    is_emerging: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    year: Mapped[int] = mapped_column(Integer, default=2024, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<PatentTrend domain={self.technology_domain} growth={self.growth_rate}%>"
