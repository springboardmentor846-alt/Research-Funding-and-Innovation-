"""
API Endpoints for Commercialization Opportunities, Industry Partners, Startup Programs, Bookmarks, and AI Recommendations.
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user, get_current_user_optional
from app.database.session import get_db
from app.models.user import User
from app.schemas.commercialization import (
    CommercializationOpportunityCreate,
    CommercializationOpportunityUpdate,
    CommercializationOpportunityResponse,
    CommercializationOpportunityListResponse,
    IndustryPartnerResponse,
    StartupRecommendationResponse,
    CommercializationRecommendationResponse,
    CollaborationResponse,
    CollaborationRequestCreate,
    CommercializationDashboardSummaryResponse,
)
from app.services.commercialization_service import CommercializationService

router = APIRouter(prefix="/commercialization", tags=["Commercialization & Industry Collaboration"])


@router.get("/opportunities", response_model=CommercializationOpportunityListResponse, summary="Search commercialization opportunities")
async def search_opportunities(
    q: Optional[str] = Query(None, description="Keyword search in title, summary, or organization"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    organization: Optional[str] = Query(None, description="Filter by organization name"),
    opportunity_type: Optional[str] = Query(None, description="Filter by opportunity type (e.g. Technology Licensing, Joint R&D)"),
    sort_by: str = Query("created_desc", description="Sort order: created_desc, funding_desc, trl_desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Search & filter commercialization opportunities with pagination."""
    user_id = current_user.id if current_user else None
    return await CommercializationService.search_opportunities(
        db,
        user_id=user_id,
        q=q,
        industry=industry,
        domain=domain,
        organization=organization,
        opportunity_type=opportunity_type,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )


@router.get("/recommendations", response_model=List[CommercializationRecommendationResponse], summary="AI commercialization recommendations")
async def get_recommended_opportunities(
    limit: int = Query(6, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate AI commercialization recommendations matched against the user's profile, papers, patents, and Innovation Score."""
    return await CommercializationService.get_recommended_opportunities(db, user_id=current_user.id, limit=limit)


@router.get("/partners", response_model=List[IndustryPartnerResponse], summary="Industry partners directory")
async def get_industry_partners(
    industry: Optional[str] = Query(None, description="Filter by industry"),
    q: Optional[str] = Query(None, description="Keyword search partner name or focus"),
    db: AsyncSession = Depends(get_db),
):
    """Fetch directory of corporate R&D labs, industry partners, and tech transfer sponsors."""
    return await CommercializationService.get_industry_partners(db, industry=industry, q=q)


@router.get("/startup-programs", response_model=List[StartupRecommendationResponse], summary="Startup accelerators and incubators")
async def get_startup_programs(
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    db: AsyncSession = Depends(get_db),
):
    """Fetch startup accelerators, incubators, seed funds, and spinout programs."""
    return await CommercializationService.get_startup_programs(db, domain=domain)


@router.get("/dashboard-summary", response_model=CommercializationDashboardSummaryResponse, summary="Commercialization dashboard data")
async def get_commercialization_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve full Commercialization Dashboard payload (Recommended Opportunities, Partners, Startup Programs, Stats)."""
    return await CommercializationService.get_dashboard_summary(db, user_id=current_user.id)


@router.get("/my-collaborations", response_model=List[CollaborationResponse], summary="User bookmarked & contacted collaborations")
async def get_my_collaborations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch all user bookmarks and submitted collaboration requests."""
    return await CommercializationService.get_user_collaborations(db, user_id=current_user.id)


@router.get("/opportunities/{opp_id}", response_model=CommercializationOpportunityResponse, summary="Get single opportunity details")
async def get_opportunity_detail(
    opp_id: uuid.UUID,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Fetch details for a single commercialization opportunity by UUID."""
    user_id = current_user.id if current_user else None
    return await CommercializationService.get_opportunity_by_id(db, opp_id=opp_id, user_id=user_id)


@router.post("/opportunities", response_model=CommercializationOpportunityResponse, status_code=status.HTTP_201_CREATED, summary="Create opportunity")
async def create_opportunity(
    data: CommercializationOpportunityCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new commercialization opportunity (Admin / Innovation Manager)."""
    return await CommercializationService.create_opportunity(db, data=data)


@router.put("/opportunities/{opp_id}", response_model=CommercializationOpportunityResponse, summary="Update opportunity")
async def update_opportunity(
    opp_id: uuid.UUID,
    data: CommercializationOpportunityUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing commercialization opportunity."""
    return await CommercializationService.update_opportunity(db, opp_id=opp_id, data=data)


@router.delete("/opportunities/{opp_id}", summary="Delete opportunity")
async def delete_opportunity(
    opp_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a commercialization opportunity."""
    return await CommercializationService.delete_opportunity(db, opp_id=opp_id)


@router.post("/bookmarks/{opp_id}", summary="Toggle opportunity bookmark")
async def toggle_bookmark(
    opp_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle bookmark state for a commercialization opportunity."""
    return await CommercializationService.toggle_bookmark(db, user_id=current_user.id, opp_id=opp_id)


@router.post("/collaborate/{opp_id}", response_model=CollaborationResponse, summary="Submit collaboration interest request")
async def submit_collaboration_request(
    opp_id: uuid.UUID,
    req: CollaborationRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a collaboration or contact request for an opportunity."""
    return await CommercializationService.submit_collaboration_request(
        db, user_id=current_user.id, opp_id=opp_id, req=req
    )
