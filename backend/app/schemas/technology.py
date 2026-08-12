"""
Technology Intelligence Pydantic Schemas
"""

from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict


class TechnologyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    domain: str
    description: Optional[str] = None
    trl_level: int
    adoption_stage: str
    market_readiness_score: float
    competitive_density: str
    key_innovators: List[str] = []
    patent_count: int = 0
    funding_volume: float = 0.0


class TechnologyMaturitySummary(BaseModel):
    trl_breakdown: Dict[int, int] # e.g. {1: 2, 2: 3, ... 9: 5}
    adoption_stages: Dict[str, int]
    emerging_technologies: List[TechnologyResponse]
