"""
API Endpoints for Technology Intelligence, Innovation Scoring, Opportunity Analysis, and Emerging Trends.
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.technology import (
    TechnologyTrendResponse,
    TechnologyTrendListResponse,
    InnovationScoreResponse,
    OpportunityAnalysisResponse,
    TechnologyDashboardSummaryResponse,
)
from app.services.technology_service import TechnologyService

router = APIRouter(prefix="/technology", tags=["Technology Intelligence"])


@router.get("/trends", response_model=TechnologyTrendListResponse, summary="Search technology trends")
async def search_technology_trends(
    q: Optional[str] = Query(None, description="Keyword search in trend name, summary, or domain"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    maturity_level: Optional[str] = Query(None, description="Filter by TRL maturity level"),
    sort_by: str = Query("growth_desc", description="Sort order: growth_desc, market_desc, trl_desc, trl_asc, created_desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Search technology trends with filtering by keyword, domain, maturity level, sorting, and pagination."""
    return await TechnologyService.search_technology_trends(
        db,
        q=q,
        domain=domain,
        maturity_level=maturity_level,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )


@router.get("/emerging", response_model=List[TechnologyTrendResponse], summary="Emerging technology trends")
async def get_emerging_technologies(
    limit: int = Query(6, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve top emerging technology trends with high annual growth rates."""
    return await TechnologyService.get_emerging_technologies(db, limit=limit)


@router.get("/innovation-score", response_model=InnovationScoreResponse, summary="User Innovation Score")
async def get_user_innovation_score(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Calculate and return the authenticated user's Innovation Score, TRL level, research strength, and patent strength."""
    return await TechnologyService.calculate_user_innovation_score(db, user_id=current_user.id)


@router.get("/opportunities", response_model=OpportunityAnalysisResponse, summary="Commercial opportunity gap analysis")
async def get_opportunity_analysis(
    limit: int = Query(6, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve market opportunity gaps and strategic R&D alignment for the authenticated user."""
    return await TechnologyService.get_opportunity_analysis(db, user_id=current_user.id, limit=limit)


@router.get("/dashboard-summary", response_model=TechnologyDashboardSummaryResponse, summary="Technology intelligence dashboard data")
async def get_technology_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve full Technology Dashboard payload (Emerging Tech, Innovation Score, Statistics, and Opportunities)."""
    return await TechnologyService.get_dashboard_summary(db, user_id=current_user.id)


@router.get("/trends/{trend_id}", response_model=TechnologyTrendResponse, summary="Get single technology trend detail")
async def get_technology_trend_detail(
    trend_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Fetch details for a single technology trend by UUID."""
    return await TechnologyService.get_trend_by_id(db, trend_id=trend_id)
