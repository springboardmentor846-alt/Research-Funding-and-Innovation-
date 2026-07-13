from pydantic import BaseModel

class TechnologyCreate(BaseModel):
    technology_name: str
    domain: str
    maturity_level: str
    trl_level: int
    adoption_rate: float
    opportunity_score: float
    publication_count: int
    patent_count: int
    trend_score: float
    competitor: str
    status: str