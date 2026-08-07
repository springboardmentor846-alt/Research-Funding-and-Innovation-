"""
Pydantic schemas for User resource — request/response validation.
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.models.user import UserRole


# ── Shared fields ─────────────────────────────────────────────────────────────
class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    role: UserRole = UserRole.RESEARCHER


# ── Create ────────────────────────────────────────────────────────────────────
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in v):
            raise ValueError("Password must contain at least one special character.")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "UserCreate":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


# ── Update ────────────────────────────────────────────────────────────────────
class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    bio: Optional[str] = Field(None, max_length=2000)
    organization: Optional[str] = Field(None, max_length=255)
    position: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=50)
    linkedin_url: Optional[str] = Field(None, max_length=512)
    website_url: Optional[str] = Field(None, max_length=512)
    avatar_url: Optional[str] = Field(None, max_length=512)


# ── Password change ───────────────────────────────────────────────────────────
class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in v):
            raise ValueError("Password must contain at least one special character.")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "PasswordChange":
        if self.new_password != self.confirm_new_password:
            raise ValueError("New passwords do not match.")
        return self


# ── Response ──────────────────────────────────────────────────────────────────
class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    is_verified: bool
    is_superuser: bool
    bio: Optional[str] = None
    organization: Optional[str] = None
    position: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    website_url: Optional[str] = None
    last_login: Optional[datetime] = None
    login_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Admin update ──────────────────────────────────────────────────────────────
class AdminUserUpdate(UserUpdate):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
