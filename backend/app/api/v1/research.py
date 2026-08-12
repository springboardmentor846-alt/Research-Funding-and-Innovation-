"""
Research Trend Intelligence & Publication Analytics API Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.dependencies.db import get_db
from app.models.research import Publication, ResearchTrend
from app.schemas.research import (
    PublicationResponse,
    ResearchTrendResponse,
    ResearchIntelligenceOverview
)

research_router = APIRouter(prefix="/research", tags=["Research Trend Intelligence"])


@research_router.get("/overview", response_model=ResearchIntelligenceOverview)
async def get_research_intelligence_overview(db: AsyncSession = Depends(get_db)):
    pub_count = (await db.execute(select(func.count(Publication.id)))).scalar() or 0
    trend_count = (await db.execute(select(func.count(ResearchTrend.id)))).scalar() or 0

    trends_res = await db.execute(select(ResearchTrend).order_by(ResearchTrend.hotspot_score.desc()).limit(6))
    trends = trends_res.scalars().all()

    pubs_res = await db.execute(select(Publication).order_by(Publication.citation_count.desc()).limit(6))
    pubs = pubs_res.scalars().all()

    hotspot_count = len([t for t in trends if t.hotspot_score >= 80.0])

    return {
        "total_publications_indexed": pub_count,
        "active_research_topics": trend_count,
        "emerging_hotspots": hotspot_count,
        "top_domains": ["Artificial Intelligence", "Quantum Computing", "Biotechnology", "Clean Energy", "Cybersecurity"],
        "emerging_trends": trends,
        "recent_publications": pubs
    }


@research_router.get("/trends", response_model=List[ResearchTrendResponse])
async def list_research_trends(
    domain: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(ResearchTrend)
    if stage:
        query = query.where(ResearchTrend.maturity_stage == stage)
    result = await db.execute(query.order_by(ResearchTrend.growth_rate_pct.desc()))
    trends = result.scalars().all()

    if domain:
        trends = [t for t in trends if domain.lower() in t.domain.lower() or domain.lower() in t.topic_name.lower()]

    return trends


@research_router.get("/publications", response_model=List[PublicationResponse])
async def list_publications(
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Publication).order_by(Publication.citation_count.desc()))
    pubs = result.scalars().all()

    if search:
        s_lower = search.lower()
        pubs = [p for p in pubs if s_lower in p.title.lower() or any(s_lower in k.lower() for k in (p.keywords or []))]

    return pubs
