"""Publication-related Pydantic schemas."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class PublicationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    abstract: Optional[str] = None
    authors: str = Field(..., min_length=1)
    keywords: Optional[str] = None
    doi: Optional[str] = None
    publisher: Optional[str] = None
    publication_date: Optional[datetime] = None
    citation_count: int = 0
    research_domain: Optional[str] = None
    venue: Optional[str] = None
    url: Optional[str] = None


class PublicationCreate(PublicationBase):
    pass


class PublicationUpdate(BaseModel):
    title: Optional[str] = None
    abstract: Optional[str] = None
    authors: Optional[str] = None
    keywords: Optional[str] = None
    doi: Optional[str] = None
    publisher: Optional[str] = None
    publication_date: Optional[datetime] = None
    citation_count: Optional[int] = None
    research_domain: Optional[str] = None
    venue: Optional[str] = None
    url: Optional[str] = None


class PublicationResponse(PublicationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime


class PublicationList(BaseModel):
    """Paginated publication list response."""
    items: List[PublicationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
