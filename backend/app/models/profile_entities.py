from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class ResearchDomain(Base):
    __tablename__ = "research_domains"

    __table_args__ = (
        UniqueConstraint("research_profile_id", "name", name="uq_research_profile_domain"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    research_profile_id: Mapped[int] = mapped_column(ForeignKey("research_profiles.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ResearchKeyword(Base):
    __tablename__ = "research_keywords"

    __table_args__ = (
        UniqueConstraint("research_profile_id", "name", name="uq_research_profile_keyword"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    research_profile_id: Mapped[int] = mapped_column(ForeignKey("research_profiles.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class TechnologyArea(Base):
    __tablename__ = "technology_areas_list"
    # Named "_list" to avoid clashing with the existing patent-side
    # technology-clusters logic elsewhere in the codebase, which is
    # unrelated (it derives clusters from patent titles, not a stored list).

    __table_args__ = (
        UniqueConstraint("research_profile_id", "name", name="uq_research_profile_technology_area"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    research_profile_id: Mapped[int] = mapped_column(ForeignKey("research_profiles.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class OrganizationInformation(Base):
    __tablename__ = "organization_information"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    research_profile_id: Mapped[int] = mapped_column(ForeignKey("research_profiles.id"), unique=True, nullable=False)

    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    organization_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )