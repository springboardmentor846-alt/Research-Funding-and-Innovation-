"""
Innovation Scoring Engine API Endpoints
Formula: Score = Novelty (30%) + Patent Strength (20%) + Tech Maturity (15%) + Market Potential (20%) + Funding Relevance (15%)
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.innovation import InnovationEvaluation
from app.schemas.innovation import (
    InnovationEvaluationRequest,
    InnovationEvaluationResponse
)
from app.services.innovation_scorer import InnovationScorerEngine

innovation_router = APIRouter(prefix="/innovation", tags=["Innovation Scoring Engine"])


@innovation_router.post("/evaluate", response_model=InnovationEvaluationResponse)
async def evaluate_innovation_project(
    data: InnovationEvaluationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Calculate weighted total score
    total_score = InnovationScorerEngine.calculate_weighted_score(
        novelty=data.research_novelty_score,
        patent_strength=data.patent_strength_score,
        tech_maturity=data.tech_maturity_score,
        market_potential=data.market_potential_score,
        funding_relevance=data.funding_relevance_score
    )

    # Generate commercialization recommendations
    recs = InnovationScorerEngine.generate_commercialization_recommendations(
        domain=data.domain,
        total_score=total_score,
        tech_maturity=data.tech_maturity_score,
        market_potential=data.market_potential_score
    )

    evaluation = InnovationEvaluation(
        user_id=current_user.id,
        project_title=data.project_title,
        domain=data.domain,
        description=data.description,
        research_novelty_score=data.research_novelty_score,
        patent_strength_score=data.patent_strength_score,
        tech_maturity_score=data.tech_maturity_score,
        market_potential_score=data.market_potential_score,
        funding_relevance_score=data.funding_relevance_score,
        total_innovation_score=total_score,
        productization_recommendations=recs["productization_recommendations"],
        licensing_opportunities=recs["licensing_opportunities"],
        startup_creation_recommendations=recs["startup_creation_recommendations"],
        industry_partnership_suggestions=recs["industry_partnership_suggestions"]
    )

    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)
    return evaluation


@innovation_router.get("/history", response_model=List[InnovationEvaluationResponse])
async def get_my_evaluation_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(InnovationEvaluation)
        .where(InnovationEvaluation.user_id == current_user.id)
        .order_by(InnovationEvaluation.evaluated_at.desc())
    )
    return result.scalars().all()
