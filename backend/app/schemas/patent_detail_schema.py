from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl


class PatentDetailBase(BaseModel):
    patent_title: str
    patent_number: Optional[str] = None
    patent_status: Optional[str] = None
    filing_date: Optional[date] = None
    publication_date: Optional[date] = None
    inventors: Optional[str] = None
    patent_url: Optional[HttpUrl] = None
    description: Optional[str] = None


class PatentDetailCreate(PatentDetailBase):
    pass


class PatentDetailUpdate(BaseModel):
    patent_title: Optional[str] = None
    patent_number: Optional[str] = None
    patent_status: Optional[str] = None
    filing_date: Optional[date] = None
    publication_date: Optional[date] = None
    inventors: Optional[str] = None
    patent_url: Optional[HttpUrl] = None
    description: Optional[str] = None


class PatentDetailResponse(PatentDetailBase):
    id: int
    portfolio_id: int

    model_config = ConfigDict(from_attributes=True)