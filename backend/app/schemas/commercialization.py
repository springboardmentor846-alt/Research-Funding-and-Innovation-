from pydantic import BaseModel


class CommercializationCreate(BaseModel):

    technology_name: str

    innovation_score: float

    technology_maturity: float

    patent_strength: float

    market_potential: float