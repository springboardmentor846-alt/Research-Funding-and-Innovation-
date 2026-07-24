from typing import Optional
from pydantic import BaseModel, ConfigDict, HttpUrl


class ResearchPaperDetailBase(BaseModel):
    paper_title: str
    journal_name: Optional[str] = None
    publication_year: Optional[int] = None
    doi: Optional[str] = None
    paper_url: Optional[HttpUrl] = None
    authors: Optional[str] = None
    abstract: Optional[str] = None


class ResearchPaperDetailCreate(ResearchPaperDetailBase):
    pass


class ResearchPaperDetailUpdate(BaseModel):
    paper_title: Optional[str] = None
    journal_name: Optional[str] = None
    publication_year: Optional[int] = None
    doi: Optional[str] = None
    paper_url: Optional[HttpUrl] = None
    authors: Optional[str] = None
    abstract: Optional[str] = None


class ResearchPaperDetailResponse(ResearchPaperDetailBase):
    id: int
    portfolio_id: int

    model_config = ConfigDict(from_attributes=True)