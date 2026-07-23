from pydantic import BaseModel, HttpUrl
from typing import Optional


class UserProfileCreate(BaseModel):
    full_name: str
    organization: Optional[str] = None
    designation: Optional[str] = None
    domain: Optional[str] = None
    skills: Optional[str] = None
    interests: Optional[str] = None
    bio: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None
    profile_image: Optional[str] = None


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    organization: Optional[str] = None
    designation: Optional[str] = None
    domain: Optional[str] = None
    skills: Optional[str] = None
    interests: Optional[str] = None
    bio: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None
    profile_image: Optional[str] = None


class UserProfileResponse(UserProfileCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True