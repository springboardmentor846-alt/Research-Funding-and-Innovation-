"""
SQLAlchemy models for Technology Intelligence & Innovation Scoring.
"""
import uuid
from datetime import datetime
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
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class TechnologyTrend(Base):
    """Emerging technology trend entity with Technology Readiness Level (TRL)."""

    __tablename__ = "technology_trends"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    technology_domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # TRL 1 to 9
    trl_level: Mapped[int] = mapped_column(Integer, default=4, nullable=False, index=True)
    maturity_level: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # e.g., "TRL 1-3 (Basic Research)"
    
    growth_rate: Mapped[float] = mapped_column(Float, nullable=False)  # e.g., 34.5 for +34.5%
    market_size_usd_b: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)  # Market size in $ Billion
    
    key_players: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    key_keywords: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    is_emerging: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    opportunity_description: Mapped[str] = mapped_column(Text, nullable=False)
    year: Mapped[int] = mapped_column(Integer, default=2025, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<TechnologyTrend name={self.name} domain={self.technology_domain} TRL={self.trl_level}>"


class InnovationScore(Base):
    """Calculated innovation scoring for a user's research & IP portfolio."""

    __tablename__ = "user_innovation_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0 to 100
    trl_level: Mapped[int] = mapped_column(Integer, default=5, nullable=False)  # 1 to 9
    research_strength: Mapped[float] = mapped_column(Float, nullable=False)  # 0 to 100
    patent_strength: Mapped[float] = mapped_column(Float, nullable=False)  # 0 to 100
    commercial_potential: Mapped[float] = mapped_column(Float, nullable=False)  # 0 to 100
    
    recommendation_summary: Mapped[str] = mapped_column(Text, nullable=False)
    breakdown_details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<InnovationScore user_id={self.user_id} score={self.overall_score} TRL={self.trl_level}>"
