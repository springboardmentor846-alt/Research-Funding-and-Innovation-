"""Funding endpoints: list/read (all users) and personalized recommendations.

Funding data is now sourced from the Funding Intelligence Service —
admin write endpoints (create/update/delete) have been removed in
favour of the per-provider sync controls exposed at
``/api/v1/funding-intel/*``.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db import get_db
from app.schemas.funding import (
    FundingResponse,
    FundingList,
    RecommendationResponse,
)
from app.services.funding_service import FundingService
from app.services.recommendation_service import RecommendationService
from app.api.v1.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/funding", tags=["Funding"])


@router.get("", response_model=FundingList)
def list_funding(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    domain: Optional[str] = None,
    funding_type: Optional[str] = None,
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all active funding opportunities (any authenticated user)."""
    skip = (page - 1) * page_size
    items, total = FundingService.list_funding(
        db,
        skip=skip,
        limit=page_size,
        search=search,
        domain=domain,
        funding_type=funding_type,
    )
    total_pages = (total + page_size - 1) // page_size if total else 0
    return FundingList(
        items=items, total=total, page=page, page_size=page_size, total_pages=total_pages
    )


@router.get("/stats/overview")
def funding_stats(
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return aggregate funding statistics (any authenticated user)."""
    return FundingService.get_stats(db)


@router.get("/recommendations/me", response_model=RecommendationResponse)
def my_recommendations(
    top_k: int = Query(10, ge=5, le=50),
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return cached personalized funding recommendations for the current user.

    The Recommendations page must not trigger recomputation on every read —
    caching is managed by ``RecommendationService``. The cache is auto-
    invalidated when:

    * the user updates research interests, publications, or profile fields,
    * new funding opportunities are synchronized (Funding Intelligence Service),
    * admin changes recommendation weights via ``PUT /admin/settings``.

    Funding records are NEVER modified by this endpoint.
    """
    recs, cache_hit = RecommendationService.get_or_generate(
        db, user=current, top_k=top_k
    )
    return RecommendationResponse(
        user_id=current.id,
        recommendations=recs,
        total=len(recs),
        generated_at=datetime.utcnow(),
        cache_hit=cache_hit,
    )


@router.post("/recommendations/refresh", response_model=RecommendationResponse)
def refresh_my_recommendations(
    top_k: int = Query(10, ge=5, le=50),
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Force a recompute of the current user's recommendations.

    Used by the manual "Refresh" button on the dashboard and the
    Recommendations page. Drops the cached rows first, then runs the
    recommender against the latest funding corpus. Unlike the GET
    endpoint, this call ALWAYS recomputes.
    """
    from app.services.funding_service import FundingService
    RecommendationService.invalidate_for_user(db, current.id)
    publications = list(current.publications or [])
    fundings = FundingService.get_recommendable(db)
    recs = RecommendationService.regenerate(
        db, user=current,
        publications=publications, fundings=fundings,
        top_k=top_k,
    )
    return RecommendationResponse(
        user_id=current.id,
        recommendations=recs,
        total=len(recs),
        generated_at=datetime.utcnow(),
        cache_hit=False,
    )


@router.get("/{funding_id}", response_model=FundingResponse)
def get_funding(
    funding_id: int,
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch a single funding opportunity by id (any authenticated user)."""
    item = FundingService.get_by_id(db, funding_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funding not found")
    return item


# ---------------------------------------------------------------------------
# NOTE: Admin write endpoints (create / update / delete / toggle) have been
# removed. Funding is sourced exclusively from the Funding Intelligence
# Service — see ``app/funding_intel/api/router.py`` for sync controls.
# ---------------------------------------------------------------------------
