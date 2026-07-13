from pydantic import BaseModel


class InnovationScoreCreate(BaseModel):

    research_novelty: float

    patent_strength: float

    technology_maturity: float

    market_potential: float

    funding_relevance: float