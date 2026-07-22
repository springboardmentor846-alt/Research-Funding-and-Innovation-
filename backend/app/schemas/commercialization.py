from pydantic import BaseModel


class CommercializationResponse(BaseModel):
    patent_title: str
    technology_name: str
    innovation_score: float

    commercialization_readiness: str
    startup_potential: str
    recommended_action: str
    recommended_funding: str
    target_industry: str
    estimated_market_potential: str
    risk_level: str

    class Config:
        from_attributes = True