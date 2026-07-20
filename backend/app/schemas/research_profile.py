from pydantic import BaseModel, Field

from datetime import date


class PublicationCreate(BaseModel):
    title: str = Field(
        min_length=2,
        max_length=500
    )

    publication_type: str | None = Field(
        default=None,
        max_length=100
    )

    authors: str | None = None

    journal_or_conference: str | None = Field(
        default=None,
        max_length=500
    )

    publisher: str | None = Field(
        default=None,
        max_length=255
    )

    publication_date: date | None = None

    doi: str | None = Field(
        default=None,
        max_length=255
    )

    url: str | None = Field(
        default=None,
        max_length=1000
    )

    abstract: str | None = Field(
        default=None,
        max_length=5000
    )

    # -------- New Fields --------

    openalex_id: str | None = Field(
        default=None,
        max_length=255
    )

    citation_count: int = Field(
        default=0,
        ge=0
    )

    research_domain: str | None = Field(
        default=None,
        max_length=255
    )

    language: str | None = Field(
        default=None,
        max_length=50
    )

    source: str | None = Field(
        default=None,
        max_length=100
    )

    is_open_access: bool = False


class PublicationUpdate(BaseModel):

    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=500
    )

    publication_type: str | None = Field(
        default=None,
        max_length=100
    )

    authors: str | None = None

    journal_or_conference: str | None = Field(
        default=None,
        max_length=500
    )

    publisher: str | None = Field(
        default=None,
        max_length=255
    )

    publication_date: date | None = None

    doi: str | None = Field(
        default=None,
        max_length=255
    )

    url: str | None = Field(
        default=None,
        max_length=1000
    )

    abstract: str | None = Field(
        default=None,
        max_length=5000
    )

    # -------- New Fields --------

    openalex_id: str | None = Field(
        default=None,
        max_length=255
    )

    citation_count: int | None = Field(
        default=None,
        ge=0
    )

    research_domain: str | None = Field(
        default=None,
        max_length=255
    )

    language: str | None = Field(
        default=None,
        max_length=50
    )

    source: str | None = Field(
        default=None,
        max_length=100
    )

    is_open_access: bool | None = None



class ResearchProfileCreate(BaseModel):
    bio: str | None = Field(
        default=None,
        max_length=2000
    )

    highest_qualification: str | None = Field(
        default=None,
        max_length=150
    )

    current_position: str | None = Field(
        default=None,
        max_length=150
    )

    organization_name: str | None = Field(
        default=None,
        max_length=255
    )

    orcid_id: str | None = Field(
        default=None,
        max_length=50
    )

class ResearchProfileUpdate(BaseModel):
    bio: str | None = Field(
        default=None,
        max_length=2000
    )

    highest_qualification: str | None = Field(
        default=None,
        max_length=150
    )

    current_position: str | None = Field(
        default=None,
        max_length=150
    )

    organization_name: str | None = Field(
        default=None,
        max_length=255
    )

    orcid_id: str | None = Field(
        default=None,
        max_length=50
    )


class ResearchDomainCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150
    )

class ResearchKeywordCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100
    )

class TechnologyAreaCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150
    )

class OrganizationInformationCreate(BaseModel):
    department: str | None = Field(
        default=None,
        max_length=255
    )

    organization_type: str | None = Field(
        default=None,
        max_length=100
    )

    city: str | None = Field(
        default=None,
        max_length=100
    )

    state: str | None = Field(
        default=None,
        max_length=100
    )

    country: str | None = Field(
        default=None,
        max_length=100
    )

    website: str | None = Field(
        default=None,
        max_length=500
    )

    description: str | None = Field(
        default=None,
        max_length=2000
    )


class OrganizationInformationUpdate(BaseModel):
    department: str | None = Field(
        default=None,
        max_length=255
    )

    organization_type: str | None = Field(
        default=None,
        max_length=100
    )

    city: str | None = Field(
        default=None,
        max_length=100
    )

    state: str | None = Field(
        default=None,
        max_length=100
    )

    country: str | None = Field(
        default=None,
        max_length=100
    )

    website: str | None = Field(
        default=None,
        max_length=500
    )

    description: str | None = Field(
        default=None,
        max_length=2000
    )


class PatentCreate(BaseModel):
    title: str = Field(
        min_length=2,
        max_length=500
    )

    patent_number: str | None = Field(
        default=None,
        max_length=255
    )

    inventors: str | None = None

    patent_office: str | None = Field(
        default=None,
        max_length=255
    )

    filing_date: date | None = None

    grant_date: date | None = None

    status: str | None = Field(
        default=None,
        max_length=100
    )

    url: str | None = Field(
        default=None,
        max_length=1000
    )

    description: str | None = Field(
        default=None,
        max_length=5000
    )


class PatentUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=500
    )

    patent_number: str | None = Field(
        default=None,
        max_length=255
    )

    inventors: str | None = None

    patent_office: str | None = Field(
        default=None,
        max_length=255
    )

    filing_date: date | None = None

    grant_date: date | None = None

    status: str | None = Field(
        default=None,
        max_length=100
    )

    url: str | None = Field(
        default=None,
        max_length=1000
    )

    description: str | None = Field(
        default=None,
        max_length=5000
    )