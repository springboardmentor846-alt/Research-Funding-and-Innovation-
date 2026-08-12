"""
Commercialization Recommendation Engine API Endpoints
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query

from app.services.innovation_scorer import InnovationScorerEngine

commercialization_router = APIRouter(prefix="/commercialization", tags=["Commercialization Advisory"])


@commercialization_router.get("/recommendations")
async def get_commercialization_recommendations(
    domain: str = Query("Artificial Intelligence"),
    total_score: float = Query(85.0),
    tech_maturity: float = Query(70.0),
    market_potential: float = Query(80.0)
) -> Dict[str, List[str]]:
    return InnovationScorerEngine.generate_commercialization_recommendations(
        domain=domain,
        total_score=total_score,
        tech_maturity=tech_maturity,
        market_potential=market_potential
    )
