"""
SQLAlchemy models for Research Profile, Publications, Patents, and Research History.
"""
import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
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


class OrganizationType(str, enum.Enum):
    UNIVERSITY = "university"
    RESEARCH_INSTITUTE = "research_institute"
    CORPORATE_RD = "corporate_rd"
    STARTUP = "startup"
    GOVERNMENT = "government"
    OTHER = "other"


class PatentStatus(str, enum.Enum):
    GRANTED = "granted"
    PENDING = "pending"
    FILED = "filed"
    EXPIRED = "expired"


class ProjectStatus(str, enum.Enum):
    ONGOING = "ongoing"
    COMPLETED = "completed"
    PROPOSED = "proposed"


class ResearchProfile(Base):
    """Rich research profile linked 1-to-1 with a User."""

    __tablename__ = "research_profiles"

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

    # Organization details
    organization_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    organization_type: Mapped[OrganizationType] = mapped_column(
        Enum(OrganizationType, name="organization_type"),
        default=OrganizationType.UNIVERSITY,
        nullable=False,
    )
    position: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Academic profile
    academic_degree: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    field_of_study: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    institution_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    graduation_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Research metrics & external IDs
    h_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    i10_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_citations: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    orcid_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    google_scholar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    scopus_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Domains, Keywords, Technology Interests (stored as JSON arrays)
    research_domains: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    keywords: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    technology_interests: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    summary_bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", backref="research_profile")
    publications: Mapped[List["Publication"]] = relationship(
        "Publication", back_populates="profile", cascade="all, delete-orphan"
    )
    patents: Mapped[List["Patent"]] = relationship(
        "Patent", back_populates="profile", cascade="all, delete-orphan"
    )
    projects: Mapped[List["ResearchProject"]] = relationship(
        "ResearchProject", back_populates="profile", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ResearchProfile user_id={self.user_id} org={self.organization_name}>"


class Publication(Base):
    """Publication entity linked to a Research Profile."""

    __tablename__ = "publications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(512), nullable=False)
    venue: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    doi: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    citations_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    authors: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    profile: Mapped["ResearchProfile"] = relationship(
        "ResearchProfile", back_populates="publications"
    )


class Patent(Base):
    """Patent entity linked to a Research Profile."""

    __tablename__ = "patents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(512), nullable=False)
    patent_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[PatentStatus] = mapped_column(
        Enum(PatentStatus, name="patent_status"),
        default=PatentStatus.PENDING,
        nullable=False,
    )
    filing_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    issue_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    profile: Mapped["ResearchProfile"] = relationship(
        "ResearchProfile", back_populates="patents"
    )


class ResearchProject(Base):
    """Research Project / History entity linked to a Research Profile."""

    __tablename__ = "research_projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(512), nullable=False)
    role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    funding_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sponsor_organization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status"),
        default=ProjectStatus.ONGOING,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    profile: Mapped["ResearchProfile"] = relationship(
        "ResearchProfile", back_populates="projects"
    )
