"""
SQLAlchemy models for Commercialization Opportunities, Industry Partners, Startup Programs, and Collaborations.
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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class CommercializationOpportunity(Base):
    """Commercialization, Licensing, and Joint R&D Opportunity."""

    __tablename__ = "commercialization_opportunities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    organization_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    industry: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    technology_domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Opportunity type: Technology Licensing, Joint R&D, Corporate Venture Capital, Startup Accelerator, Contract Research
    opportunity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    detailed_description: Mapped[str] = mapped_column(Text, nullable=False)
    
    trl_requirement: Mapped[int] = mapped_column(Integer, default=4, nullable=False)  # TRL 1 to 9
    estimated_funding_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_person: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    
    key_keywords: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    matching_technologies: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    deadline: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<CommercializationOpportunity title={self.title[:30]} org={self.organization_name}>"


class IndustryPartner(Base):
    """Industry partner, corporate R&D lab, or technology buyer."""

    __tablename__ = "industry_partners"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    industry: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    organization_type: Mapped[str] = mapped_column(String(100), nullable=False)  # Corporate R&D, Tech Giant, VC, Research Institute
    
    technology_focus: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    website_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    collaboration_types: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<IndustryPartner name={self.name} industry={self.industry}>"


class StartupRecommendation(Base):
    """Startup accelerator, incubator, or spinout funding program."""

    __tablename__ = "startup_recommendations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    program_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    organizer: Mapped[str] = mapped_column(String(255), nullable=False)
    program_type: Mapped[str] = mapped_column(String(100), nullable=False)  # Accelerator, Incubator, Seed VC, Spinout Program
    technology_domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    funding_amount_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    equity_taken_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    duration_months: Mapped[int] = mapped_column(Integer, default=6, nullable=False)
    
    description: Mapped[str] = mapped_column(Text, nullable=False)
    eligibility_criteria: Mapped[str] = mapped_column(Text, nullable=False)
    website_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    deadline: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<StartupRecommendation name={self.program_name} type={self.program_type}>"


class Collaboration(Base):
    """User bookmark or expressed interest / collaboration request."""

    __tablename__ = "collaborations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("commercialization_opportunities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    status: Mapped[str] = mapped_column(String(50), default="bookmarked", nullable=False)  # bookmarked, contacted, under_review
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    opportunity: Mapped["CommercializationOpportunity"] = relationship("CommercializationOpportunity")

    def __repr__(self) -> str:
        return f"<Collaboration user_id={self.user_id} opp_id={self.opportunity_id} status={self.status}>"
