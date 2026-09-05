from pydantic import BaseModel
from typing import Optional


class NamedEntityCreate(BaseModel):
    name: str


class ResearchDomainResponse(BaseModel):
    id: int
    research_profile_id: int
    name: str

    class Config:
        from_attributes = True


class ResearchKeywordResponse(BaseModel):
    id: int
    research_profile_id: int
    name: str

    class Config:
        from_attributes = True


class TechnologyAreaResponse(BaseModel):
    id: int
    research_profile_id: int
    name: str

    class Config:
        from_attributes = True


class OrganizationInfoUpdate(BaseModel):
    department: Optional[str] = None
    organization_type: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None


class OrganizationInfoResponse(BaseModel):
    id: int
    research_profile_id: int
    department: Optional[str] = None
    organization_type: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True