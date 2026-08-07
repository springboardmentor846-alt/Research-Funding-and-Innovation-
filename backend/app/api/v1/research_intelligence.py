"""
API Endpoints for Research Intelligence, Papers Search, Trending Topics, and AI Recommendations.
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user, get_current_user_optional
from app.database.session import get_db
from app.models.user import User
from app.schemas.research_intelligence import (
    ResearchPaperResponse,
    ResearchPaperListResponse,
    ResearchTrendResponse,
    PaperRecommendationResponse,
    ResearchIntelligenceDashboardSummaryResponse,
)
from app.services.research_intelligence_service import ResearchIntelligenceService

router = APIRouter(prefix="/research-intelligence", tags=["Research Intelligence"])


@router.get("/search", response_model=ResearchPaperListResponse, summary="Search scientific research papers")
async def search_research_papers(
    q: Optional[str] = Query(None, description="Keyword search in paper title, abstract, or venue"),
    domain: Optional[str] = Query(None, description="Filter by research domain"),
    year_min: Optional[int] = Query(None, ge=1900, le=2100, description="Minimum publication year"),
    year_max: Optional[int] = Query(None, ge=1900, le=2100, description="Maximum publication year"),
    author: Optional[str] = Query(None, description="Filter by author name"),
    sort_by: str = Query("citations_desc", description="Sort order: citations_desc, year_desc, year_asc, created_desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await ResearchIntelligenceService.search_papers(
        db,
        q=q,
        domain=domain,
        year_min=year_min,
        year_max=year_max,
        author=author,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )


@router.get("/recommendations", response_model=List[PaperRecommendationResponse], summary="AI recommended research papers")
async def get_recommended_papers(
    limit: int = Query(6, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ResearchIntelligenceService.get_recommended_papers(db, user_id=current_user.id, limit=limit)


@router.get("/trending", response_model=List[ResearchTrendResponse], summary="Trending research topics")
async def get_trending_research(
    limit: int = Query(6, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    return await ResearchIntelligenceService.get_trending_research(db, limit=limit)


@router.get("/emerging", response_model=List[ResearchTrendResponse], summary="Emerging technology topics")
async def get_emerging_topics(
    limit: int = Query(6, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    return await ResearchIntelligenceService.get_emerging_topics(db, limit=limit)


@router.get("/dashboard-summary", response_model=ResearchIntelligenceDashboardSummaryResponse, summary="Research intelligence dashboard cards")
async def get_research_intelligence_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ResearchIntelligenceService.get_dashboard_summary(db, user_id=current_user.id)


@router.get("/papers/{paper_id}", response_model=ResearchPaperResponse, summary="Get single research paper details")
async def get_paper_details(
    paper_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await ResearchIntelligenceService.get_paper_by_id(db, paper_id=paper_id)
