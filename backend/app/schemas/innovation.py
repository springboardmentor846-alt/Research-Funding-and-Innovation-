from pydantic import BaseModel


class InnovationResponse(BaseModel):
    patent_title: str
    technology_name: str
    research_domain: str

    innovation_score: float
    innovation_level: str
    commercialization_probability: str
    recommendation: str

    class Config:
        from_attributes = True