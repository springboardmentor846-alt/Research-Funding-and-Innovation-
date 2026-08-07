"""
API Endpoints for Patent Intelligence: Search, Details, Trends, Analytics, and AI Recommendations.
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.patent import (
    PatentRecordResponse,
    PatentRecordListResponse,
    PatentTrendResponse,
    PatentAnalyticsResponse,
    PatentRecommendationResponse,
    PatentDashboardSummaryResponse,
)
from app.services.patent_service import PatentService

router = APIRouter(prefix="/patents", tags=["Patent Intelligence"])


@router.get("/search", response_model=PatentRecordListResponse, summary="Search patent database")
async def search_patents(
    q: Optional[str] = Query(None, description="Keyword search in patent title, abstract, number, or organization"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    inventor: Optional[str] = Query(None, description="Filter by inventor name"),
    organization: Optional[str] = Query(None, description="Filter by assignee organization"),
    publication_year: Optional[int] = Query(None, ge=1900, le=2100, description="Filter by publication year"),
    status: Optional[str] = Query(None, description="Filter by status: Granted, Pending, Expired"),
    sort_by: str = Query("citations_desc", description="Sort order: citations_desc, year_desc, year_asc, claims_desc, created_desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Search patents across keywords, domain, inventor, organization, year, and status with pagination."""
    return await PatentService.search_patents(
        db,
        q=q,
        domain=domain,
        inventor=inventor,
        organization=organization,
        publication_year=publication_year,
        status=status,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )


@router.get("/recommendations", response_model=List[PatentRecommendationResponse], summary="AI patent recommendations")
async def get_recommended_patents(
    limit: int = Query(6, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate AI patent recommendations matched with the authenticated user's Research Profile."""
    return await PatentService.get_recommended_patents(db, user_id=current_user.id, limit=limit)


@router.get("/trending", response_model=List[PatentTrendResponse], summary="Patent technology trends")
async def get_patent_trends(
    limit: int = Query(6, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve top trending technology domains and emerging innovation metrics."""
    return await PatentService.get_patent_trends(db, limit=limit)


@router.get("/analytics", response_model=PatentAnalyticsResponse, summary="Patent analytics and statistics")
async def get_patent_analytics(
    db: AsyncSession = Depends(get_db),
):
    """Get aggregate statistics: top organizations, technology domain distribution, publication years, and status breakdown."""
    return await PatentService.get_patent_analytics(db)


@router.get("/dashboard-summary", response_model=PatentDashboardSummaryResponse, summary="Patent dashboard summary data")
async def get_patent_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve full Patent Dashboard view dataset (Statistics, Recent Patents, Top Orgs, Trends, and Recommendations)."""
    return await PatentService.get_dashboard_summary(db, user_id=current_user.id)


@router.get("/{patent_id}", response_model=PatentRecordResponse, summary="Get single patent record details")
async def get_patent_details(
    patent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get comprehensive details for a single patent record by UUID."""
    return await PatentService.get_patent_by_id(db, patent_id=patent_id)
