from pydantic import BaseModel
from typing import Optional


class PublicationCreate(BaseModel):
    title: str
    authors: str
    publication_type: str
    journal_or_conference: str
    publication_year: int
    doi: Optional[str] = None
    abstract: str
    keywords: str
    pdf_url: Optional[str] = None


class PublicationResponse(PublicationCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True
