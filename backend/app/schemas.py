from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    
    
    
class ResearchProfileCreate(BaseModel):
    organization: str
    research_domain: str
    technology_area: str
    keywords: str
    publication_count: int
    patents: int


class ResearchProfileResponse(BaseModel):
    id: int
    organization: str
    research_domain: str
    technology_area: str
    keywords: str
    publication_count: int
    patents: int

    class Config:
        from_attributes = True


class ResearchProfileUpdate(BaseModel):
    organization: str
    research_domain: str
    technology_area: str
    keywords: str
    publication_count: int
    patents: int    
    
    
class PublicationCreate(BaseModel):
    title: str
    authors: str
    journal: str
    publication_year: int
    doi: str


class PublicationUpdate(BaseModel):
    title: str
    authors: str
    journal: str
    publication_year: int
    doi: str


class PublicationResponse(BaseModel):
    id: int
    title: str
    authors: str
    journal: str
    publication_year: int
    doi: str

    class Config:
        from_attributes = True    
        
        
        
class PatentCreate(BaseModel):
    title: str
    assignee: str
    filing_date: str
    patent_number: str
    technology_domain: str


class PatentUpdate(BaseModel):
    title: str
    assignee: str
    filing_date: str
    patent_number: str
    technology_domain: str


class PatentResponse(BaseModel):
    id: int
    title: str
    assignee: str
    filing_date: str
    patent_number: str
    technology_domain: str

    class Config:
        from_attributes = True 
        
        
class DashboardSummary(BaseModel):
    research_profiles: int
    publications: int
    patents: int
    funding_opportunities: int
    

class FundingOpportunityCreate(BaseModel):
    title: str
    funding_agency: str
    research_domain: str
    technology_area: str
    keywords: str
    amount: str
    deadline: str
    eligibility: str
    description: str | None = None
    link: str | None = None


class FundingOpportunityUpdate(BaseModel):
    title: str
    funding_agency: str
    research_domain: str
    technology_area: str
    keywords: str
    amount: str
    deadline: str
    eligibility: str
    description: str | None = None
    link: str | None = None


class FundingOpportunityResponse(BaseModel):
    id: int
    title: str
    funding_agency: str
    research_domain: str
    technology_area: str
    keywords: str
    amount: str
    deadline: str
    eligibility: str
    description: str | None = None
    link: str | None = None
    
    score: int | None = None
    reason: list[str] | None = None

    class Config:
        from_attributes = True    
        
class GrantMatchResponse(BaseModel):
    title: str
    funding_agency: str
    research_domain: str
    technology_area: str
    match_score: int            
  
class PublicationTrend(BaseModel):
    year: int
    count: int

    class Config:
        from_attributes = True    