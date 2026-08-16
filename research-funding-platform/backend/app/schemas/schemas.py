from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    role: str = "Researcher" # Researcher, Startup Founder, Innovation Manager, Administrator
    organization: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)

# --- User & Profile Schemas ---
class UserRead(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    organization: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    organization: Optional[str] = None
    role: Optional[str] = None

class ResearchProfileBase(BaseModel):
    domains: Optional[str] = None
    keywords: Optional[str] = None
    organization: Optional[str] = None
    bio: Optional[str] = None
    publications_count: Optional[int] = 0
    patents_count: Optional[int] = 0
    h_index: Optional[int] = 0

class ResearchProfileCreate(ResearchProfileBase):
    pass

class ResearchProfileRead(ResearchProfileBase):
    id: int
    user_id: int
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Funding Opportunity Schemas ---
class FundingOpportunityBase(BaseModel):
    title: str
    agency: str
    grant_type: str
    amount: float
    deadline: str
    description: str
    eligibility_criteria: str
    keywords: Optional[str] = None
    url: Optional[str] = None
    target_roles: Optional[str] = "Researcher,Startup Founder,Innovation Manager"

class FundingOpportunityCreate(FundingOpportunityBase):
    pass

class FundingOpportunityRead(FundingOpportunityBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Publication Schemas ---
class PublicationBase(BaseModel):
    title: str
    authors: str
    journal: str
    publication_date: str
    citations_count: int = 0
    impact_factor: float = 1.0
    abstract: str
    keywords: Optional[str] = None
    doi: Optional[str] = None

class PublicationCreate(PublicationBase):
    pass

class PublicationRead(PublicationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Patent Schemas ---
class PatentBase(BaseModel):
    patent_number: str
    title: str
    assignee: str
    filing_date: str
    grant_date: Optional[str] = None
    status: str = "Active"
    claims_count: int = 1
    abstract: str
    tech_field: str

class PatentCreate(PatentBase):
    pass

class PatentRead(PatentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Tech Trend Schemas ---
class TechTrendBase(BaseModel):
    technology_name: str
    category: str
    growth_rate: float
    readiness_level: int = Field(..., ge=1, le=9)
    adoption_stage: str = "Emerging"
    market_size_est: str
    description: str

class TechTrendCreate(TechTrendBase):
    pass

class TechTrendRead(TechTrendBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Innovation Score Schemas ---
class InnovationScoreCalculate(BaseModel):
    entity_type: str # Research, Startup, Patent, Technology
    entity_name: str
    novelty_score: float = Field(..., ge=0, le=100)
    patent_strength: float = Field(..., ge=0, le=100)
    tech_maturity: float = Field(..., ge=0, le=100)
    market_potential: float = Field(..., ge=0, le=100)
    funding_relevance: float = Field(..., ge=0, le=100)

class InnovationScoreRead(BaseModel):
    id: int
    entity_type: str
    entity_name: str
    novelty_score: float
    patent_strength: float
    tech_maturity: float
    market_potential: float
    funding_relevance: float
    overall_score: float
    recommendations: Optional[str]
    computed_at: datetime

    class Config:
        from_attributes = True

# --- Commercialization Opportunity Schemas ---
class CommercializationBase(BaseModel):
    title: str
    insight_type: str
    description: str
    target_industry: str
    estimated_value: str
    readiness: str = "Medium"
    contact_email: Optional[str] = None

class CommercializationCreate(CommercializationBase):
    pass

class CommercializationRead(CommercializationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Report & Notification Schemas ---
class ReportCreate(BaseModel):
    title: str
    report_type: str
    format: str = "PDF"
    parameters: Optional[Dict[str, Any]] = None

class ReportRead(BaseModel):
    id: int
    title: str
    report_type: str
    format: str
    parameters: Optional[Dict[str, Any]]
    file_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationRead(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
