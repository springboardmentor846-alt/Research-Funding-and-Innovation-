"""Collaboration and Funding History Pydantic schemas."""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


# ----- Research Interests -----
class ResearchInterestBase(BaseModel):
    """Shared fields for research-interest payloads."""
    name: str = Field(..., min_length=1, max_length=120)


class ResearchInterestCreate(ResearchInterestBase):
    """Create payload. `is_custom` is inferred when missing — see service."""
    is_custom: Optional[bool] = None


class ResearchInterestUpdate(BaseModel):
    """Update payload: only the display name is mutable."""
    name: str = Field(..., min_length=1, max_length=120)


class ResearchInterestResponse(BaseModel):
    """A single research interest as returned to clients."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    is_custom: bool
    source: Optional[str] = None
    position: int = 0
    created_at: datetime


class ResearchInterestList(BaseModel):
    """List payload for research interests."""
    items: List[ResearchInterestResponse]
    total: int


class ResearchInterestReplaceAll(BaseModel):
    """Bulk replace payload — replaces the user's full interest set in one call."""
    items: List[str] = Field(default_factory=list)


class ResearchDomainCatalog(BaseModel):
    """Catalog of predefined research domains the user can choose from."""
    domains: List[str] = Field(default_factory=list)


# ----- Collaborations -----


# ----- Collaborations -----
class CollaborationBase(BaseModel):
    collaborator_name: str = Field(..., min_length=1, max_length=255)
    collaborator_email: Optional[str] = None
    collaborator_affiliation: Optional[str] = None
    project_title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str = "active"


class CollaborationCreate(CollaborationBase):
    pass


class CollaborationUpdate(BaseModel):
    collaborator_name: Optional[str] = None
    collaborator_email: Optional[str] = None
    collaborator_affiliation: Optional[str] = None
    project_title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None


class CollaborationResponse(CollaborationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime


class CollaborationList(BaseModel):
    items: List[CollaborationResponse]
    total: int


# ----- Funding History -----
class FundingHistoryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    organization: Optional[str] = None
    amount: Optional[float] = None
    currency: str = "USD"
    status: str = "awarded"
    awarded_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = None
    funding_id: Optional[int] = None


class FundingHistoryCreate(FundingHistoryBase):
    pass


class FundingHistoryUpdate(BaseModel):
    title: Optional[str] = None
    organization: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    awarded_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = None
    funding_id: Optional[int] = None


class FundingHistoryResponse(FundingHistoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime


class FundingHistoryList(BaseModel):
    items: List[FundingHistoryResponse]
    total: int
    total_amount: float = 0.0
