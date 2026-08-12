"""
Research Profile Pydantic Schemas
"""

from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class ResearchProfileCreate(BaseModel):
    organization: Optional[str] = None
    department: Optional[str] = None
    academic_title: Optional[str] = None
    bio: Optional[str] = None
    research_domains: List[str] = []
    keywords: List[str] = []
    technology_areas: List[str] = []


class ResearchProfileUpdate(BaseModel):
    organization: Optional[str] = None
    department: Optional[str] = None
    academic_title: Optional[str] = None
    bio: Optional[str] = None
    research_domains: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    technology_areas: Optional[List[str]] = None
    total_publications: Optional[int] = None
    total_citations: Optional[int] = None
    h_index: Optional[int] = None
    i10_index: Optional[int] = None


class ResearchProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    organization: Optional[str] = None
    department: Optional[str] = None
    academic_title: Optional[str] = None
    bio: Optional[str] = None
    research_domains: List[str] = []
    keywords: List[str] = []
    technology_areas: List[str] = []
    total_publications: int = 0
    total_citations: int = 0
    h_index: int = 0
    i10_index: int = 0
