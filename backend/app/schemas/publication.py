from pydantic import BaseModel
from typing import Optional


class PublicationCreate(BaseModel):
    title: str
    year: int
    authors: str
    citation_count: Optional[int] = 0
    research_domain: str
    keywords: str
    organization: str


class PublicationResponse(PublicationCreate):
    id: int

    class Config:
        from_attributes = True
