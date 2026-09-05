from pydantic import BaseModel
from typing import Optional


class PublicationCreate(BaseModel):
    title: str
    authors: Optional[str] = None
    year: Optional[str] = None
    source: Optional[str] = None
    link: Optional[str] = None


class PublicationResponse(BaseModel):
    id: int
    profile_id: int
    title: str
    authors: Optional[str] = None
    year: Optional[str] = None
    source: Optional[str] = None
    link: Optional[str] = None
    pdf_path: Optional[str] = None
    source_type: str = "own"

    class Config:
        from_attributes = True


class ExternalPublicationImport(BaseModel):
    """Used when saving an OpenAlex search result into the Research Library."""
    title: str
    authors: Optional[str] = None
    year: Optional[str] = None
    source: Optional[str] = None
    link: Optional[str] = None