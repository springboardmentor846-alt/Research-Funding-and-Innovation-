from pydantic import BaseModel


class TechnologyBase(BaseModel):
    technology_name: str
    category: str
    description: str
    maturity_level: str
    growth_score: float
    adoption_rate: float


class TechnologyCreate(TechnologyBase):
    pass


class TechnologyUpdate(TechnologyBase):
    pass


class TechnologyResponse(TechnologyBase):
    id: int

    class Config:
        from_attributes = True