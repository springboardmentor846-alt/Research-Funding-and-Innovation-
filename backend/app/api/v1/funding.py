"""
API Endpoints for Funding Opportunity Discovery, Search, Recommendations, Bookmarks, and Alerts.
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user, get_current_user_optional
from app.database.session import get_db
from app.models.user import User
from app.schemas.funding import (
    FundingOpportunityCreate,
    FundingOpportunityUpdate,
    FundingOpportunityResponse,
    FundingOpportunityListResponse,
    FundingAlertCreate,
    FundingAlertResponse,
    FundingRecommendationResponse,
    FundingDashboardSummaryResponse,
)
from app.services.funding_service import FundingService

router = APIRouter(prefix="/funding", tags=["Funding Opportunity Discovery"])


@router.get("/search", response_model=FundingOpportunityListResponse, summary="Search and filter funding opportunities")
async def search_funding_opportunities(
    q: Optional[str] = Query(None, description="Keyword search in title, funder, or description"),
    domain: Optional[str] = Query(None, description="Filter by research domain"),
    funding_type: Optional[str] = Query(None, description="Filter by funding type (Grant, Fellowship, Equity, etc.)"),
    country: Optional[str] = Query(None, description="Filter by eligible country"),
    sort_by: str = Query("deadline_asc", description="Sort order: deadline_asc, deadline_desc, amount_desc, created_desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user.id if current_user else None
    return await FundingService.search_opportunities(
        db,
        user_id=user_id,
        q=q,
        domain=domain,
        funding_type=funding_type,
        country=country,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )


@router.get("/recommendations", response_model=List[FundingRecommendationResponse], summary="AI Recommended funding opportunities")
async def get_recommended_funding(
    limit: int = Query(6, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await FundingService.get_recommendations(db, user_id=current_user.id, limit=limit)


@router.get("/dashboard-summary", response_model=FundingDashboardSummaryResponse, summary="Funding dashboard cards & widgets")
async def get_funding_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await FundingService.get_dashboard_summary(db, user_id=current_user.id)


@router.get("/bookmarks/me", response_model=List[FundingOpportunityResponse], summary="Get logged-in user bookmarked grants")
async def get_user_bookmarks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await FundingService.get_user_bookmarks(db, user_id=current_user.id)


@router.post("/{opportunity_id}/bookmark", summary="Toggle bookmark on a funding opportunity")
async def toggle_funding_bookmark(
    opportunity_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await FundingService.toggle_bookmark(db, user_id=current_user.id, opportunity_id=opportunity_id)


@router.get("/alerts/me", response_model=List[FundingAlertResponse], summary="Get user funding search alerts")
async def get_user_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await FundingService.get_user_alerts(db, user_id=current_user.id)


@router.post("/alerts", response_model=FundingAlertResponse, status_code=status.HTTP_201_CREATED, summary="Create a funding search alert")
async def create_funding_alert(
    data: FundingAlertCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await FundingService.create_alert(db, user_id=current_user.id, data=data)


@router.delete("/alerts/{alert_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a funding search alert")
async def delete_funding_alert(
    alert_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await FundingService.delete_alert(db, user_id=current_user.id, alert_id=alert_id)
    return None


@router.get("/{opportunity_id}", response_model=FundingOpportunityResponse, summary="Get single funding opportunity details")
async def get_funding_opportunity_details(
    opportunity_id: uuid.UUID,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user.id if current_user else None
    return await FundingService.get_opportunity_by_id(db, opportunity_id=opportunity_id, user_id=user_id)


@router.post("", response_model=FundingOpportunityResponse, status_code=status.HTTP_201_CREATED, summary="Create funding opportunity")
async def create_funding_opportunity(
    data: FundingOpportunityCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await FundingService.create_opportunity(db, data=data)
