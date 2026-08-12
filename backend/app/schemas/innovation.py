"""
Innovation Scoring & Commercialization Pydantic Schemas
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class InnovationEvaluationRequest(BaseModel):
    project_title: str = Field(..., min_length=3, max_length=255)
    domain: str = Field(..., min_length=2, max_length=255)
    description: str = Field(..., min_length=10)
    
    # Sub-scores provided or auto-computed (0 to 100)
    research_novelty_score: float = Field(default=75.0, ge=0.0, le=100.0)   # 30%
    patent_strength_score: float = Field(default=70.0, ge=0.0, le=100.0)    # 20%
    tech_maturity_score: float = Field(default=65.0, ge=0.0, le=100.0)     # 15%
    market_potential_score: float = Field(default=80.0, ge=0.0, le=100.0)   # 20%
    funding_relevance_score: float = Field(default=85.0, ge=0.0, le=100.0)  # 15%


class CommercializationAdvisory(BaseModel):
    productization_recommendations: List[str]
    licensing_opportunities: List[str]
    startup_creation_recommendations: List[str]
    industry_partnership_suggestions: List[str]


class InnovationEvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    project_title: str
    domain: str
    description: str
    
    research_novelty_score: float
    patent_strength_score: float
    tech_maturity_score: float
    market_potential_score: float
    funding_relevance_score: float
    
    total_innovation_score: float
    
    productization_recommendations: List[str] = []
    licensing_opportunities: List[str] = []
    startup_creation_recommendations: List[str] = []
    industry_partnership_suggestions: List[str] = []
    
    evaluated_at: datetime
