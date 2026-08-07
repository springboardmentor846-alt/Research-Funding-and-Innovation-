"""
Pydantic schemas for Research Profile, Publications, Patents, and Projects.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, HttpUrl, Field

from app.models.research_profile import OrganizationType, PatentStatus, ProjectStatus


# ── Publication Schemas ───────────────────────────────────────────────────────
class PublicationBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=512)
    venue: Optional[str] = Field(None, max_length=255)
    year: Optional[int] = Field(None, ge=1900, le=2100)
    doi: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = Field(None, max_length=512)
    citations_count: int = Field(0, ge=0)
    abstract: Optional[str] = None
    authors: Optional[str] = Field(None, max_length=512)


class PublicationCreate(PublicationBase):
    pass


class PublicationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=512)
    venue: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    citations_count: Optional[int] = Field(None, ge=0)
    abstract: Optional[str] = None
    authors: Optional[str] = None


class PublicationResponse(PublicationBase):
    id: uuid.UUID
    profile_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Patent Schemas ────────────────────────────────────────────────────────────
class PatentBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=512)
    patent_number: Optional[str] = Field(None, max_length=100)
    status: PatentStatus = PatentStatus.PENDING
    filing_date: Optional[str] = Field(None, max_length=50)
    issue_date: Optional[str] = Field(None, max_length=50)
    url: Optional[str] = Field(None, max_length=512)
    abstract: Optional[str] = None


class PatentCreate(PatentBase):
    pass


class PatentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=512)
    patent_number: Optional[str] = None
    status: Optional[PatentStatus] = None
    filing_date: Optional[str] = None
    issue_date: Optional[str] = None
    url: Optional[str] = None
    abstract: Optional[str] = None


class PatentResponse(PatentBase):
    id: uuid.UUID
    profile_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Research Project / History Schemas ───────────────────────────────────────
class ResearchProjectBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=512)
    role: Optional[str] = Field(None, max_length=255)
    summary: Optional[str] = None
    start_date: Optional[str] = Field(None, max_length=50)
    end_date: Optional[str] = Field(None, max_length=50)
    funding_amount: Optional[float] = Field(None, ge=0)
    sponsor_organization: Optional[str] = Field(None, max_length=255)
    status: ProjectStatus = ProjectStatus.ONGOING


class ResearchProjectCreate(ResearchProjectBase):
    pass


class ResearchProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=512)
    role: Optional[str] = None
    summary: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    funding_amount: Optional[float] = None
    sponsor_organization: Optional[str] = None
    status: Optional[ProjectStatus] = None


class ResearchProjectResponse(ResearchProjectBase):
    id: uuid.UUID
    profile_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Research Profile Schemas ──────────────────────────────────────────────────
class ResearchProfileUpdate(BaseModel):
    organization_name: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    organization_type: Optional[OrganizationType] = None
    position: Optional[str] = Field(None, max_length=255)

    academic_degree: Optional[str] = Field(None, max_length=255)
    field_of_study: Optional[str] = Field(None, max_length=255)
    institution_name: Optional[str] = Field(None, max_length=255)
    graduation_year: Optional[int] = Field(None, ge=1950, le=2100)

    h_index: Optional[int] = Field(None, ge=0)
    i10_index: Optional[int] = Field(None, ge=0)
    total_citations: Optional[int] = Field(None, ge=0)
    orcid_id: Optional[str] = Field(None, max_length=100)
    google_scholar_url: Optional[str] = Field(None, max_length=512)
    scopus_id: Optional[str] = Field(None, max_length=100)

    research_domains: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    technology_interests: Optional[List[str]] = None

    summary_bio: Optional[str] = None


class ResearchProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    full_name: Optional[str] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None

    organization_name: Optional[str] = None
    department: Optional[str] = None
    organization_type: OrganizationType
    position: Optional[str] = None

    academic_degree: Optional[str] = None
    field_of_study: Optional[str] = None
    institution_name: Optional[str] = None
    graduation_year: Optional[int] = None

    h_index: int = 0
    i10_index: int = 0
    total_citations: int = 0
    orcid_id: Optional[str] = None
    google_scholar_url: Optional[str] = None
    scopus_id: Optional[str] = None

    research_domains: List[str] = []
    keywords: List[str] = []
    technology_interests: List[str] = []

    summary_bio: Optional[str] = None
    avatar_url: Optional[str] = None

    publications: List[PublicationResponse] = []
    patents: List[PatentResponse] = []
    projects: List[ResearchProjectResponse] = []

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResearcherSearchResult(BaseModel):
    items: List[ResearchProfileResponse]
    total: int
    page: int
    page_size: int
