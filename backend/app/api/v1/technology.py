"""
Technology Intelligence & TRL Maturity API Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies.db import get_db
from app.models.technology import Technology
from app.schemas.technology import TechnologyResponse, TechnologyMaturitySummary

technology_router = APIRouter(prefix="/technology", tags=["Technology Intelligence & TRL"])


@technology_router.get("/summary", response_model=TechnologyMaturitySummary)
async def get_technology_maturity_summary(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Technology))
    techs = result.scalars().all()

    trl_counts = {i: 0 for i in range(1, 10)}
    stages_counts = {"R&D": 0, "Pilot": 0, "Commercial": 0, "Widespread": 0}

    for t in techs:
        if 1 <= t.trl_level <= 9:
            trl_counts[t.trl_level] = trl_counts.get(t.trl_level, 0) + 1
        stages_counts[t.adoption_stage] = stages_counts.get(t.adoption_stage, 0) + 1

    return {
        "trl_breakdown": trl_counts,
        "adoption_stages": stages_counts,
        "emerging_technologies": techs
    }


@technology_router.get("/list", response_model=List[TechnologyResponse])
async def list_technologies(
    domain: Optional[str] = Query(None),
    min_trl: Optional[int] = Query(None, ge=1, le=9),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Technology)
    if min_trl:
        stmt = stmt.where(Technology.trl_level >= min_trl)
    result = await db.execute(stmt.order_by(Technology.market_readiness_score.desc()))
    techs = result.scalars().all()

    if domain:
        techs = [t for t in techs if domain.lower() in t.domain.lower() or domain.lower() in t.name.lower()]

    return techs
