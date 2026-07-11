from pydantic import BaseModel


class ResearchTrendCreate(BaseModel):
    research_domain: str
    year: int
    publications: int
    trend_score: int


class ResearchTrendResponse(BaseModel):
    id: int
    research_domain: str
    year: int
    publications: int
    trend_score: int

    class Config:
        from_attributes = True