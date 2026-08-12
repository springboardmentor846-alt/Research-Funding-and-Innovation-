"""
Funding Opportunity & Grant Application Models Definition
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.db.base_class import Base


class GrantType(str, enum.Enum):
    GOVERNMENT_GRANT = "Government Grants"
    RESEARCH_COUNCIL = "Research Councils"
    INNOVATION_FUND = "Innovation Funds"
    STARTUP_ACCELERATOR = "Startup Accelerators"
    VENTURE_PROGRAM = "Venture Programs"
    INTERNATIONAL_AGENCY = "International Funding Agencies"


class FundingOpportunity(Base):
    """
    Funding Opportunity entity representing grants, seed funding, and innovation calls.
    """
    __tablename__ = "funding_opportunities"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    agency: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    opportunity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    total_funding_amount: Mapped[float] = mapped_column(Float, default=0.0)
    min_award: Mapped[float] = mapped_column(Float, default=0.0)
    max_award: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    application_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="OPEN", index=True) # OPEN, CLOSING_SOON, CLOSED
    
    # Metadata collections for matching
    eligibility_criteria: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    target_domains: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    target_keywords: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    eligible_applicant_types: Mapped[list] = mapped_column(JSON, default=list, nullable=False) # Researcher, Startup Founder, University

    def __repr__(self) -> str:
        return f"<FundingOpportunity(id={self.id}, title='{self.title}', agency='{self.agency}')>"


class SavedGrant(Base):
    """
    Saved / Tracked Funding Grant for a user with calculated match score.
    """
    __tablename__ = "saved_grants"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    grant_id: Mapped[str] = mapped_column(String(36), ForeignKey("funding_opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    match_score: Mapped[float] = mapped_column(Float, default=0.0) # Match score percentage (0-100)
    status: Mapped[str] = mapped_column(String(50), default="SAVED") # SAVED, APPLYING, SUBMITTED
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<SavedGrant(user_id={self.user_id}, grant_id={self.grant_id}, score={self.match_score})>"
