from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ResearchProfile(Base):
    __tablename__ = "research_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                     unique=True, nullable=False, index=True)

    headline = Column(String, nullable=True)
    bio = Column(Text, nullable=True)

    research_domains = Column(JSONB, nullable=False, server_default="[]")
    keywords = Column(JSONB, nullable=False, server_default="[]")
    technology_areas = Column(JSONB, nullable=False, server_default="[]")

    organization = Column(String, nullable=True)
    organization_type = Column(String, nullable=True)
    country = Column(String, nullable=True)
    website = Column(String, nullable=True)
    orcid_id = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    publications = relationship("Publication", back_populates="profile",
                                cascade="all, delete-orphan")
    patents = relationship("Patent", back_populates="profile",
                           cascade="all, delete-orphan")


class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("research_profiles.id", ondelete="CASCADE"),
                        nullable=False, index=True)

    title = Column(String, nullable=False)
    authors = Column(JSONB, nullable=False, server_default="[]")
    venue = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    doi = Column(String, nullable=True)
    url = Column(String, nullable=True)
    citation_count = Column(Integer, nullable=True, default=0)
    abstract = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    profile = relationship("ResearchProfile", back_populates="publications")


class Patent(Base):
    __tablename__ = "patents"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("research_profiles.id", ondelete="CASCADE"),
                        nullable=False, index=True)

    title = Column(String, nullable=False)
    assignee = Column(String, nullable=True)
    patent_number = Column(String, nullable=True)
    filing_date = Column(Date, nullable=True)
    classification = Column(String, nullable=True)
    technology_domain = Column(String, nullable=True)
    citation_count = Column(Integer, nullable=True, default=0)
    url = Column(String, nullable=True)
    abstract = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    profile = relationship("ResearchProfile", back_populates="patents")
