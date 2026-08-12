"""
Funding Opportunity Discovery & Grant Matching API Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.funding import FundingOpportunity, SavedGrant
from app.schemas.funding import (
    FundingOpportunityResponse,
    GrantEligibilityRequest,
    GrantEligibilityResponse,
    SavedGrantResponse
)
from app.services.funding_engine import FundingEngine

funding_router = APIRouter(prefix="/funding", tags=["Funding Discovery & Grants"])


@funding_router.get("/opportunities", response_model=List[FundingOpportunityResponse])
async def list_funding_opportunities(
    domain: Optional[str] = Query(None, description="Filter by domain keyword"),
    opportunity_type: Optional[str] = Query(None, description="Filter by grant type"),
    db: AsyncSession = Depends(get_db)
):
    query = select(FundingOpportunity)
    if opportunity_type:
        query = query.where(FundingOpportunity.opportunity_type == opportunity_type)
    
    result = await db.execute(query.order_by(FundingOpportunity.created_at.desc()))
    grants = result.scalars().all()

    if domain:
        domain_lower = domain.lower()
        grants = [
            g for g in grants 
            if any(domain_lower in d.lower() for d in (g.target_domains or [])) 
            or any(domain_lower in k.lower() for k in (g.target_keywords or []))
            or domain_lower in g.title.lower()
        ]

    return grants


@funding_router.get("/opportunities/{grant_id}", response_model=FundingOpportunityResponse)
async def get_funding_opportunity(grant_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FundingOpportunity).where(FundingOpportunity.id == grant_id))
    grant = result.scalars().first()
    if not grant:
        raise HTTPException(status_code=404, detail="Funding Opportunity not found")
    return grant


@funding_router.post("/eligibility-match", response_model=List[GrantEligibilityResponse])
async def match_grant_eligibility(
    data: GrantEligibilityRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(FundingOpportunity))
    grants = result.scalars().all()

    matched_results = []
    for g in grants:
        res = FundingEngine.calculate_eligibility_score(
            opportunity=g,
            user_domains=data.research_domains,
            user_keywords=data.keywords,
            applicant_role=data.organization_type
        )
        matched_results.append(res)

    matched_results.sort(key=lambda x: x["match_score"], reverse=True)
    return matched_results


@funding_router.post("/saved", response_model=SavedGrantResponse)
async def save_grant_for_user(
    grant_id: str,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if already saved
    existing = await db.execute(
        select(SavedGrant).where(SavedGrant.user_id == current_user.id, SavedGrant.grant_id == grant_id)
    )
    saved = existing.scalars().first()

    if not saved:
        saved = SavedGrant(
            user_id=current_user.id,
            grant_id=grant_id,
            match_score=85.0,
            status="SAVED",
            notes=notes
        )
        db.add(saved)
        await db.commit()
        await db.refresh(saved)

    return saved


@funding_router.get("/saved/my-grants", response_model=List[SavedGrantResponse])
async def get_my_saved_grants(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(SavedGrant).where(SavedGrant.user_id == current_user.id))
    saved_list = result.scalars().all()
    return saved_list
