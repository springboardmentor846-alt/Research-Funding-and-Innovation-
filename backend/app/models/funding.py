"""
SQLAlchemy models for Funding Opportunities, Bookmarks, and Search Alerts.
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
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class FundingOpportunity(Base):
    """Funding opportunity grant/award dataset item."""

    __tablename__ = "funding_opportunities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    funder_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    funder_type: Mapped[str] = mapped_column(String(100), nullable=False, default="Government")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    amount_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    amount_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    
    deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    funding_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True, default="Grant")
    
    eligible_countries: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    research_domains: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    keywords: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    application_url: Mapped[str] = mapped_column(String(512), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    bookmarks: Mapped[list["FundingBookmark"]] = relationship(
        back_populates="opportunity", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<FundingOpportunity id={self.id} title={self.title[:30]} funder={self.funder_name}>"


class FundingBookmark(Base):
    """User saved/bookmarked funding opportunity."""

    __tablename__ = "funding_bookmarks"
    __table_args__ = (
        UniqueConstraint("user_id", "funding_opportunity_id", name="uq_user_funding_bookmark"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    funding_opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("funding_opportunities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User")
    opportunity: Mapped["FundingOpportunity"] = relationship("FundingOpportunity", back_populates="bookmarks")


class FundingAlert(Base):
    """User funding discovery alert criteria."""

    __tablename__ = "funding_alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    keywords: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    research_domains: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    funding_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    frequency: Mapped[str] = mapped_column(String(50), default="weekly", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User")
