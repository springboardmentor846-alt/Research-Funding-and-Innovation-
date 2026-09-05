from pydantic import BaseModel
from typing import Optional


class ResearchProfileCreate(BaseModel):
    research_domains: Optional[str] = None
    keywords: Optional[str] = None
    publications: Optional[str] = None
    patents: Optional[str] = None
    technology_areas: Optional[str] = None
    organization_name: Optional[str] = None
    orcid_id: Optional[str] = None


class ResearchProfileResponse(BaseModel):
    id: int
    user_id: int
    research_domains: Optional[str] = None
    keywords: Optional[str] = None
    publications: Optional[str] = None
    patents: Optional[str] = None
    technology_areas: Optional[str] = None
    organization_name: Optional[str] = None
    orcid_id: Optional[str] = None

    class Config:
        from_attributes = True