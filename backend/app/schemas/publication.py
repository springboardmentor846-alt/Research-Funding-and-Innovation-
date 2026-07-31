from datetime import date

from pydantic import BaseModel, ConfigDict


class PublicationCreate(BaseModel):

    title: str

    publication_type: str | None = None

    authors: str | None = None

    journal_or_conference: str | None = None

    publisher: str | None = None

    publication_date: date | None = None

    doi: str | None = None

    url: str | None = None

    abstract: str | None = None


class PublicationUpdate(BaseModel):

    title: str | None = None

    publication_type: str | None = None

    authors: str | None = None

    journal_or_conference: str | None = None

    publisher: str | None = None

    publication_date: date | None = None

    doi: str | None = None

    url: str | None = None

    abstract: str | None = None


class PublicationResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    title: str

    publication_type: str | None = None

    authors: str | None = None

    journal_or_conference: str | None = None

    publisher: str | None = None

    publication_date: date | None = None

    doi: str | None = None

    url: str | None = None

    abstract: str | None = None

    citation_count: int = 0

    research_domain: str | None = None

    language: str | None = None

    source: str | None = None

    is_open_access: bool = False