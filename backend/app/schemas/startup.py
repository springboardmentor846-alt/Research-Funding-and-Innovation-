from pydantic import BaseModel
from typing import Optional


class StartupProfileBase(BaseModel):
    startup_name: str
    tagline: Optional[str] = None

    industry: Optional[str] = None
    stage: Optional[str] = "Idea"

    founded_year: Optional[int] = None
    funding_stage: Optional[str] = "Bootstrapped"

    startup_email: Optional[str] = None
    phone_number: Optional[str] = None

    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    location: Optional[str] = None

    description: Optional[str] = None
    problem_statement: Optional[str] = None
    solution: Optional[str] = None

    technology_stack: Optional[str] = None
    research_interests: Optional[str] = None

    funding_needed: Optional[str] = None
    team_size: Optional[int] = 1

    pitch_deck_url: Optional[str] = None
    logo_url: Optional[str] = None


class StartupCreate(StartupProfileBase):
    pass


class StartupUpdate(StartupProfileBase):
    pass


class StartupResponse(StartupProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
