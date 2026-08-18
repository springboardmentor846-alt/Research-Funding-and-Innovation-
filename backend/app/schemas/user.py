"""User-related Pydantic schemas."""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

from app.models.user import UserRole
from app.schemas.profile import ResearchInterestResponse


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None
    role: UserRole = UserRole.RESEARCHER


class UserCreate(UserBase):
    """User registration schema."""
    password: str = Field(..., min_length=8, max_length=128)
    affiliation: Optional[str] = None


class UserUpdate(BaseModel):
    """User profile update schema."""
    full_name: Optional[str] = None
    affiliation: Optional[str] = None
    research_interests: Optional[str] = None
    skills: Optional[str] = None
    bio: Optional[str] = None
    orcid: Optional[str] = None
    avatar_url: Optional[str] = None


class UserLogin(BaseModel):
    """User login schema."""
    username: str
    password: str


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Token refresh request schema."""
    refresh_token: str


class UserResponse(UserBase):
    """User response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_verified: bool
    affiliation: Optional[str] = None
    # Legacy CSV field — kept for backward compatibility with existing callers
    # (Profile.jsx reads `user.research_interests` as a string). Always present
    # because the structured interests list is mirrored into this field by the
    # research_interest_service sync helper.
    research_interests: Optional[str] = None
    # New: structured list of research interests. Same name, different shape;
    # we expose it under a distinct key so we don't break legacy clients.
    interests: List[ResearchInterestResponse] = Field(default_factory=list)
    skills: Optional[str] = None
    bio: Optional[str] = None
    orcid: Optional[str] = None
    h_index: int
    i10_index: int
    citation_count: int
    avatar_url: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None


class UserStats(BaseModel):
    """User statistics schema."""
    total_publications: int
    total_citations: int
    h_index: int
    i10_index: int
    recommendations_count: int
    funding_awarded: int
    funding_awarded_amount: float = 0.0
    collaborations_count: int = 0
