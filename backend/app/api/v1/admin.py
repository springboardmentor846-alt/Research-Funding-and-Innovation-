"""Admin portal endpoints.

All routes require the admin role. The admin portal is responsible for
platform-wide management: dashboards, user/funding/publication/patent
monitoring, AI recommendation oversight, reports, and system settings.

The admin does NOT receive personalized AI recommendations or own any
publications, patents, or research profile.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, or_, distinct
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
import csv
import io

from app.db import get_db
from app.api.v1.deps import get_current_user, require_role
from app.core.logging import logger
from app.models.user import User, UserRole
from app.models.publication import Publication
from app.models.funding import Funding
from app.models.recommendation import Recommendation
from app.models.collaboration import Collaboration
from app.models.funding_history import FundingHistory
from app.services.user_service import UserService
from app.services.funding_service import FundingService
from app.services.publication_service import PublicationService
from app.services.recommendation_service import RecommendationService
from app.schemas.user import UserResponse
from app.schemas.funding import FundingResponse
from app.schemas.publication import PublicationResponse

router = APIRouter(prefix="/admin", tags=["Admin Portal"])


# ---------------------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------------------
@router.get("/dashboard/summary")
def admin_dashboard_summary(
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Aggregated KPIs for the admin landing page."""
    user_stats = UserService.admin_stats(db)
    funding_stats = FundingService.admin_stats(db)
    pub_stats = PublicationService.admin_publication_stats(db)
    rec_count = db.query(func.count(Recommendation.id)).scalar() or 0
    funding_total = funding_stats["total_funding"]
    pub_total = pub_stats["total_publications"]

    # Average recommendation score (where present)
    avg_score = (
        db.query(func.avg(Recommendation.similarity_score)).scalar() or 0
    )

    # Patents: surfaced from the live ``patents`` table populated by
    # the Patent Intelligence Service.
    from app.patents.services.landscape_service import PatentLandscapeService
    landscape = PatentLandscapeService(db).overview()
    patent_total = int(landscape.get("total_patents", 0))
    patent_citations = int(landscape.get("total_citations", 0))

    return {
        "users": user_stats,
        "funding": funding_stats,
        "publications": pub_stats,
        "patents": {
            "total_patents": patent_total,
            "total_citations": patent_citations,
        },
        "ai_recommendations": {
            "total_generated": int(rec_count),
            "avg_similarity_score": round(float(avg_score), 4),
        },
        "kpis": {
            "total_users": user_stats["total_users"],
            "total_funding": funding_total,
            "total_publications": pub_total,
            "total_patents": patent_total,
            "total_recommendations": int(rec_count),
            "active_users": user_stats["active_users"],
            "active_30d": user_stats["active_30d"],
        },
    }


@router.get("/dashboard/recent-activity")
def admin_recent_activity(
    limit: int = Query(20, ge=1, le=100),
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Recent platform activity across users, publications, funding, recommendations."""
    activities: list[dict] = []

    # Newest users
    recent_users = (
        db.query(User).order_by(User.created_at.desc()).limit(limit).all()
    )
    for u in recent_users:
        activities.append({
            "type": "user_signup",
            "at": u.created_at.isoformat() if u.created_at else None,
            "actor": u.username,
            "description": f"New {u.role.value} account: {u.username}",
        })

    # Newest publications
    recent_pubs = (
        db.query(Publication)
        .order_by(Publication.created_at.desc())
        .limit(limit)
        .all()
    )
    for p in recent_pubs:
        activities.append({
            "type": "publication_added",
            "at": p.created_at.isoformat() if p.created_at else None,
            "actor": f"publication#{p.id}",
            "description": f"Publication added: {p.title[:80]}",
        })

    # Newest funding
    recent_fund = (
        db.query(Funding).order_by(Funding.created_at.desc()).limit(limit).all()
    )
    for f in recent_fund:
        activities.append({
            "type": "funding_added",
            "at": f.created_at.isoformat() if f.created_at else None,
            "actor": "platform",
            "description": f"Funding added: {f.title[:80]}",
        })

    # Newest recommendations
    recent_recs = (
        db.query(Recommendation)
        .order_by(Recommendation.created_at.desc())
        .limit(limit)
        .all()
    )
    for r in recent_recs:
        activities.append({
            "type": "recommendation_generated",
            "at": r.created_at.isoformat() if r.created_at else None,
            "actor": f"user#{r.user_id}",
            "description": f"Recommendation generated (score {round(r.similarity_score, 2)})",
        })

    # Sort and cap
    activities.sort(key=lambda a: a.get("at") or "", reverse=True)
    return {"items": activities[:limit]}


# ---------------------------------------------------------------------------
# USER MANAGEMENT
# ---------------------------------------------------------------------------
@router.get("/users")
def admin_list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Paginated + filterable user list for the admin console."""
    skip = (page - 1) * page_size
    items, total = UserService.list_users_paginated(
        db, skip=skip, limit=page_size, search=search, role=role, is_active=is_active
    )
    total_pages = (total + page_size - 1) // page_size if total else 0
    return {
        "items": [
            {
                "id": u.id,
                "email": u.email,
                "username": u.username,
                "full_name": u.full_name,
                "role": u.role.value,
                "is_active": u.is_active,
                "is_verified": u.is_verified,
                "affiliation": u.affiliation,
                "h_index": u.h_index,
                "i10_index": u.i10_index,
                "citation_count": u.citation_count,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "last_login": u.last_login.isoformat() if u.last_login else None,
            }
            for u in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/users/{user_id}")
def admin_get_user(
    user_id: int,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Detailed view of a single user (admin only)."""
    user = UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    pub_count = db.query(func.count(Publication.id)).filter(Publication.owner_id == user_id).scalar() or 0
    rec_count = db.query(func.count(Recommendation.id)).filter(Recommendation.user_id == user_id).scalar() or 0
    collab_count = db.query(func.count(Collaboration.id)).filter(Collaboration.owner_id == user_id).scalar() or 0
    fund_hist_count = db.query(func.count(FundingHistory.id)).filter(FundingHistory.owner_id == user_id).scalar() or 0
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "role": user.role.value,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "affiliation": user.affiliation,
        "research_interests": user.research_interests,
        "skills": user.skills,
        "bio": user.bio,
        "orcid": user.orcid,
        "h_index": user.h_index,
        "i10_index": user.i10_index,
        "citation_count": user.citation_count,
        "avatar_url": user.avatar_url,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "stats": {
            "publications_count": int(pub_count),
            "recommendations_count": int(rec_count),
            "collaborations_count": int(collab_count),
            "funding_history_count": int(fund_hist_count),
        },
    }


# ---------------------------------------------------------------------------
# FUNDING INTELLIGENCE (read-only)
# ---------------------------------------------------------------------------
# Admin CRUD has been removed. Funding opportunities are now sourced from
# external providers via the Funding Intelligence Service. Admin surfaces
# live under /admin/funding-intel/* — see ``app/funding_intel/api/router.py``.
#
# We keep a thin admin/funding alias for backward compatibility with any
# clients that still hit it: it simply forwards to the Funding Intel
# read-only listing.
from app.funding_intel.services.sync import SyncEngine  # noqa: E402


@router.get("/funding")
def admin_list_funding(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    search: Optional[str] = None,
    domain: Optional[str] = None,
    funding_type: Optional[str] = None,
    country: Optional[str] = None,
    source: Optional[str] = None,
    is_active: Optional[bool] = None,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Backward-compatible admin funding list.

    Returns the same shape as before but reads exclusively from the
    Funding Intelligence Service-managed ``funding`` table. Use the
    /admin/funding-intel/* endpoints for richer sync controls.
    """
    return _legacy_admin_list_funding(
        db,
        page=page,
        page_size=page_size,
        search=search,
        domain=domain,
        funding_type=funding_type,
        country=country,
        source=source,
        is_active=is_active,
    )


def _legacy_admin_list_funding(
    db: Session,
    *,
    page: int,
    page_size: int,
    search: Optional[str],
    domain: Optional[str],
    funding_type: Optional[str],
    country: Optional[str],
    source: Optional[str],
    is_active: Optional[bool],
):
    skip = (page - 1) * page_size
    items, total = FundingService.admin_list_funding(
        db,
        skip=skip,
        limit=page_size,
        search=search,
        domain=domain,
        funding_type=funding_type,
        country=country,
        source=source,
        is_active=is_active,
    )
    total_pages = (total + page_size - 1) // page_size if total else 0
    return {
        "items": [
            {
                "id": f.id,
                "title": f.title,
                "description": f.description,
                "organization": f.organization,
                "country": f.country,
                "research_domain": f.research_domain,
                "funding_type": f.funding_type,
                "amount_min": f.amount_min,
                "amount_max": f.amount_max,
                "currency": f.currency,
                "application_deadline": f.application_deadline.isoformat() if f.application_deadline else None,
                "url": f.url,
                "keywords": f.keywords,
                "is_active": f.is_active,
                "created_at": f.created_at.isoformat() if f.created_at else None,
                # ``source`` is the provider name for the FIRST FundingSource
                # this row is linked to (admin list does not paginate sources
                # — use the Funding Intel view for the full breakdown).
                "source": (f.sources[0].source if getattr(f, "sources", None) else None),
            }
            for f in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "source": "funding_intel",
        "note": "Funding is read-only. Use /admin/funding-intel/* for sync controls.",
    }


@router.get("/funding/stats")
def admin_funding_stats(
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    return FundingService.admin_stats(db)


# ---------------------------------------------------------------------------
# ADMIN FUNDING CRUD
# ---------------------------------------------------------------------------
# The "Imported Funding" page is read-only by default (rows are managed by
# the Funding Intelligence Service), but admins can also manually create,
# edit, or delete funding opportunities — e.g. to fix a typo in a
# provider-supplied record, or to add a local opportunity that is not in
# any external source. Every CRUD op invalidates the recommendation cache
# so the next read picks up the change.
@router.post("/funding", response_model=FundingResponse, status_code=status.HTTP_201_CREATED)
def admin_create_funding(
    payload: dict,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Manually create a funding opportunity. Admin only."""
    from app.schemas.funding import FundingCreate
    try:
        create_payload = FundingCreate(**payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {exc}")
    funding = FundingService.create(db, create_payload)
    # Cache invalidation: new candidate in the corpus means existing
    # recommendations may now be missing a match.
    RecommendationService.invalidate_all(db)
    return funding


@router.put("/funding/{funding_id}", response_model=FundingResponse)
def admin_update_funding(
    funding_id: int,
    payload: dict,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Update an existing funding opportunity (full or partial). Admin only."""
    from app.schemas.funding import FundingUpdate
    funding = FundingService.get_by_id(db, funding_id)
    if not funding:
        raise HTTPException(status_code=404, detail="Funding not found")
    try:
        update_payload = FundingUpdate(**payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {exc}")
    updated = FundingService.update(db, funding, update_payload)
    # Cache invalidation: an edited title/keywords/description shifts scores.
    RecommendationService.invalidate_all(db)
    return updated


@router.patch("/funding/{funding_id}", response_model=FundingResponse)
def admin_patch_funding(
    funding_id: int,
    payload: dict,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Partial update — same shape as PUT, but the spec asked us to verify
    both PATCH and DELETE are reachable. We delegate to the same service
    method so the behaviour is identical to PUT."""
    from app.schemas.funding import FundingUpdate
    funding = FundingService.get_by_id(db, funding_id)
    if not funding:
        raise HTTPException(status_code=404, detail="Funding not found")
    try:
        update_payload = FundingUpdate(**payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {exc}")
    updated = FundingService.update(db, funding, update_payload)
    RecommendationService.invalidate_all(db)
    return updated


@router.delete("/funding/{funding_id}", status_code=status.HTTP_200_OK)
def admin_delete_funding(
    funding_id: int,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Permanently remove a funding opportunity. Admin only."""
    funding = FundingService.get_by_id(db, funding_id)
    if not funding:
        raise HTTPException(status_code=404, detail="Funding not found")
    FundingService.delete(db, funding)
    # Cache invalidation: removed row may be referenced by cached recs.
    RecommendationService.invalidate_all(db)
    return {"message": "Funding deleted", "id": funding_id}


# ---------------------------------------------------------------------------
# MANUAL FUNDING SYNC (Funding Intelligence Service)
# ---------------------------------------------------------------------------
# Spec'd name: ``POST /admin/sync-funding``. This endpoint triggers an
# immediate funding-opportunity sync from the enabled external providers
# (NIH, NSF, Grants.gov, OpenAlex, ...). It is a thin alias of
# ``/api/v1/funding-intel/sync`` so the spec'd URL works as a one-liner.
@router.post("/sync-funding", status_code=status.HTTP_202_ACCEPTED)
async def admin_sync_funding(
    payload: Optional[dict] = None,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Manually trigger a funding-opportunity sync from external APIs.

    Body (all optional): ``{"provider": "nih", "mode": "incremental", "force": false}``
    - ``provider``: restrict the run to one provider (default: all enabled).
    - ``mode``: ``"incremental"`` (default) or ``"full"``.
    - ``force``: bypass the global pause flag.
    """
    payload = payload or {}
    provider = payload.get("provider")
    mode = payload.get("mode", "incremental")
    force = bool(payload.get("force", False))
    if mode not in ("incremental", "full"):
        raise HTTPException(status_code=400, detail="mode must be 'incremental' or 'full'")

    engine = SyncEngine(db=db)
    try:
        result = await engine.run(provider=provider, mode=mode, force=force)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover - safety net
        logger.exception(f"sync-funding failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

    return {
        "message": "Sync completed",
        "status": result.get("status"),
        "mode": result.get("mode"),
        "started_at": result.get("started_at"),
        "finished_at": result.get("finished_at"),
        "providers": result.get("providers", []),
        "note": "Funding data is sourced exclusively from the Funding Intelligence Service.",
    }


# ---------------------------------------------------------------------------
# PUBLICATION MONITORING
# ---------------------------------------------------------------------------
@router.get("/publications/stats")
def admin_publication_stats(
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    return PublicationService.admin_publication_stats(db)


@router.delete("/publications/{pub_id}", status_code=status.HTTP_200_OK)
def admin_delete_publication(
    pub_id: int,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Remove a publication. Admin only — for duplicates, spam, or invalid records.
    Researchers cannot delete from this endpoint; the legitimate delete is on
    /publications/{pub_id} and is owner-gated.
    """
    pub = PublicationService.get_by_id(db, pub_id)
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")
    PublicationService.delete(db, pub)
    return {"message": "Publication removed by administrator", "id": pub_id}


# ---------------------------------------------------------------------------
# PATENT MONITORING
# ---------------------------------------------------------------------------
# The existing /patents endpoints serve the mock dataset to any authenticated
# user. Admin monitoring reuses that data and adds aggregate statistics so the
# admin console can present a clear "system overview".
@router.get("/patents/overview")
def admin_patent_overview(
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Patent monitoring overview built from the live patent corpus."""
    from app.patents.services.landscape_service import PatentLandscapeService
    landscape = PatentLandscapeService(db).overview()
    # The admin table also needs the list of individual items, with
    # the same shape the existing UI expects.
    rows = db.query(Patent).order_by(Patent.publication_year.desc(), Patent.citations.desc()).limit(500).all()
    items = [
        {
            "id": p.patent_number,
            "patent_number": p.patent_number,
            "title": p.title,
            "abstract": p.abstract,
            "source": p.source,
            "year": p.publication_year,
            "technology": p.technology_area,
            "citations": p.citations,
            "assignee": p.assignee,
            "country": p.country,
        }
        for p in rows
    ]
    return {
        "total_patents": landscape["total_patents"],
        "total_citations": landscape["total_citations"],
        "by_source": landscape["by_source"],
        "by_technology": landscape["by_technology"],
        "by_year": landscape["by_year"],
        "items": items,
    }


# ---------------------------------------------------------------------------
# AI RECOMMENDATION MONITORING
# ---------------------------------------------------------------------------
@router.get("/recommendations/stats")
def admin_recommendation_stats(
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Platform-wide recommendation analytics."""
    total = db.query(func.count(Recommendation.id)).scalar() or 0
    avg_sim = db.query(func.avg(Recommendation.similarity_score)).scalar() or 0
    avg_rule = db.query(func.avg(Recommendation.rule_score)).scalar() or 0
    unique_users = db.query(func.count(distinct(Recommendation.user_id))).scalar() or 0
    unique_funding = db.query(func.count(distinct(Recommendation.funding_id))).scalar() or 0
    # Score buckets
    rows = (
        db.query(
            func.count(Recommendation.id).filter(Recommendation.similarity_score >= 0.7).label("high"),
            func.count(Recommendation.id).filter(Recommendation.similarity_score >= 0.4, Recommendation.similarity_score < 0.7).label("medium"),
            func.count(Recommendation.id).filter(Recommendation.similarity_score < 0.4).label("low"),
        )
        .one()
    )
    high, medium, low = rows
    return {
        "total_recommendations": int(total),
        "unique_users": int(unique_users),
        "unique_funding": int(unique_funding),
        "avg_similarity_score": round(float(avg_sim), 4),
        "avg_rule_score": round(float(avg_rule), 4),
        "by_quality": {
            "high": int(high or 0),
            "medium": int(medium or 0),
            "low": int(low or 0),
        },
    }


@router.get("/recommendations")
def admin_list_recommendations(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user_id: Optional[int] = None,
    funding_id: Optional[int] = None,
    min_score: Optional[float] = None,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Paginated view of all generated recommendations across the platform."""
    query = db.query(Recommendation)
    if user_id is not None:
        query = query.filter(Recommendation.user_id == user_id)
    if funding_id is not None:
        query = query.filter(Recommendation.funding_id == funding_id)
    if min_score is not None:
        query = query.filter(Recommendation.similarity_score >= min_score)
    total = query.count()
    items = (
        query.order_by(Recommendation.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    total_pages = (total + page_size - 1) // page_size if total else 0
    return {
        "items": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "funding_id": r.funding_id,
                "similarity_score": r.similarity_score,
                "rule_score": r.rule_score,
                "matching_keywords": r.matching_keywords,
                "explanation": r.explanation,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.delete("/recommendations/{rec_id}", status_code=status.HTTP_200_OK)
def admin_delete_recommendation(
    rec_id: int,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Remove an individual incorrect/stale recommendation record (admin only).
    Does NOT regenerate recommendations for users.
    """
    rec = db.query(Recommendation).filter(Recommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    db.delete(rec)
    db.commit()
    return {"message": "Recommendation removed", "id": rec_id}


@router.post("/recommendations/regenerate")
def admin_regenerate_recommendations(
    payload: dict,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Regenerate recommendations for a single user or the whole platform.
    Body: {"user_id": int}  -- user_id is required.
    """
    from app.services.recommendation_service import RecommendationService
    from app.services.funding_service import FundingService as _FS
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    user = UserService.get_by_id(db, int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    pubs = user.publications
    fundings = _FS.get_all_active(db)
    recs = RecommendationService.regenerate(
        db, user=user, publications=pubs, fundings=fundings, top_k=20
    )
    return {
        "message": "Recommendations regenerated",
        "user_id": user.id,
        "count": len(recs),
    }


# ---------------------------------------------------------------------------
# REPORTS & EXPORTS
# ---------------------------------------------------------------------------
def _csv_response(filename: str, headers: list, rows: list[list]) -> StreamingResponse:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/reports/users/export")
def export_users_report(
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    headers = ["ID", "Username", "Email", "Full Name", "Role", "Active", "Verified", "Affiliation", "Created At", "Last Login"]
    rows = [
        [
            u.id, u.username, u.email, u.full_name or "", u.role.value,
            "yes" if u.is_active else "no", "yes" if u.is_verified else "no",
            u.affiliation or "",
            u.created_at.isoformat() if u.created_at else "",
            u.last_login.isoformat() if u.last_login else "",
        ]
        for u in users
    ]
    return _csv_response("users_report.csv", headers, rows)


@router.get("/reports/funding/export")
def export_funding_report(
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    items = db.query(Funding).order_by(Funding.created_at.desc()).all()
    headers = ["ID", "Title", "Organization", "Country", "Domain", "Type", "Amount Min", "Amount Max", "Currency", "Active", "Deadline"]
    rows = [
        [
            f.id, f.title, f.organization or "", f.country or "",
            f.research_domain or "", f.funding_type or "",
            f.amount_min or "", f.amount_max or "", f.currency or "USD",
            "yes" if f.is_active else "no",
            f.application_deadline.isoformat() if f.application_deadline else "",
        ]
        for f in items
    ]
    return _csv_response("funding_report.csv", headers, rows)


@router.get("/reports/publications/export")
def export_publications_report(
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    items = db.query(Publication).order_by(Publication.created_at.desc()).all()
    headers = ["ID", "Title", "Authors", "DOI", "Publisher", "Research Domain", "Citations", "Owner ID", "Created At"]
    rows = [
        [
            p.id, p.title, p.authors, p.doi or "", p.publisher or "",
            p.research_domain or "", p.citation_count,
            p.owner_id,
            p.created_at.isoformat() if p.created_at else "",
        ]
        for p in items
    ]
    return _csv_response("publications_report.csv", headers, rows)


@router.get("/reports/patents/export")
def export_patents_report(
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Patent CSV export built from the live ``patents`` table.

    Iterates every row in the canonical patent corpus (the same data
    the Patent Analytics Dashboard reads from), so the report always
    reflects real ingested data — never a hardcoded list.
    """
    from app.models.patent import Patent

    rows = (
        db.query(Patent)
        .order_by(Patent.publication_year.desc(), Patent.citations.desc())
        .all()
    )
    headers = [
        "Patent Number",
        "Title",
        "Source",
        "Publication Year",
        "Technology Area",
        "Assignee",
        "Country",
        "Citations",
        "URL",
    ]
    body = [
        [
            p.patent_number or "",
            p.title or "",
            p.source or "",
            p.publication_year if p.publication_year is not None else "",
            p.technology_area or "",
            p.assignee or "",
            p.country or "",
            int(p.citations or 0),
            p.url or "",
        ]
        for p in rows
    ]
    return _csv_response("patents_report.csv", headers, body)


# ---------------------------------------------------------------------------
# SYSTEM SETTINGS
# ---------------------------------------------------------------------------
# In-memory settings store. These represent platform-level configuration
# exposed in the admin Settings page. For a production deployment you would
# persist this to the database; for this demo a process-level dict is enough
# to back the UI and keep the architecture honest.
_PLATFORM_SETTINGS = {
    "platform_name": "Research Funding & Innovation Intelligence Platform",
    "platform_version": "1.0.0",
    "support_email": "support@research-platform.local",
    "maintenance_mode": False,
    "allow_registration": True,
    "default_user_role": UserRole.RESEARCHER.value,
    "ai_config": {
        "recommender_top_k": 10,
        "similarity_threshold": 0.08,
        "rule_weight": 0.0,
        "similarity_weight": 0.6,
        "enabled": True,
        # New: per-signal weights consumed by the recommendation engine at
        # request time. Admins can tune via PUT /admin/settings without a
        # restart. See ``app.ai.weights.DEFAULT_AI_WEIGHTS`` for the
        # authoritative defaults.
        "recommender_weights": {
            "publication_similarity": 0.60,
            "user_interests": 0.40,
            "similarity_threshold": 0.08,
            "min_final_score": 0.05,
            # Legacy keys — kept visible for transparency, not used in v2.
            "research_keywords": 0.00,
            "eligibility": 0.00,
            "history_penalty": 0.00,
        },
    },
    "funding_categories": [
        "grant", "fellowship", "accelerator", "prize", "scholarship",
    ],
    "research_domains": [
        "Artificial Intelligence", "Medical AI", "Computer Science",
        "Public Health", "Mental Health", "Defense AI", "Entrepreneurship",
        "Social Impact", "Oncology", "Climate", "Energy Storage",
        "Quantum Computing", "Biotechnology",
    ],
    "session_timeout_minutes": 60,
    "max_pagination_size": 200,
}


@router.get("/settings")
def get_settings(
    _admin: User = Depends(require_role(UserRole.ADMIN)),
):
    return _PLATFORM_SETTINGS


@router.put("/settings")
def update_settings(
    payload: dict,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Update platform settings. Only known keys are accepted.

    If the admin changes anything inside ``ai_config`` (weights, threshold,
    top_k) the cached recommendations are dropped so the next user load
    reflects the new configuration.
    """
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Body must be a JSON object")
    # Allowlist: only update keys we know about
    updatable_top = {
        "platform_name", "support_email", "maintenance_mode",
        "allow_registration", "default_user_role", "funding_categories",
        "research_domains", "session_timeout_minutes", "max_pagination_size",
    }
    ai_changed = False
    for k, v in payload.items():
        if k in updatable_top:
            _PLATFORM_SETTINGS[k] = v
        elif k == "ai_config" and isinstance(v, dict):
            _PLATFORM_SETTINGS["ai_config"].update(v)
            ai_changed = True
    if ai_changed:
        from app.services.recommendation_service import RecommendationService
        RecommendationService.invalidate_all(db)
    return _PLATFORM_SETTINGS


@router.post("/settings/funding-categories")
def add_funding_category(
    payload: dict,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
):
    name = (payload.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    if name in _PLATFORM_SETTINGS["funding_categories"]:
        raise HTTPException(status_code=400, detail="Category already exists")
    _PLATFORM_SETTINGS["funding_categories"].append(name)
    return _PLATFORM_SETTINGS


@router.delete("/settings/funding-categories/{name}")
def remove_funding_category(
    name: str,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
):
    if name in _PLATFORM_SETTINGS["funding_categories"]:
        _PLATFORM_SETTINGS["funding_categories"].remove(name)
    return _PLATFORM_SETTINGS


@router.post("/settings/research-domains")
def add_research_domain(
    payload: dict,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
):
    name = (payload.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    if name in _PLATFORM_SETTINGS["research_domains"]:
        raise HTTPException(status_code=400, detail="Domain already exists")
    _PLATFORM_SETTINGS["research_domains"].append(name)
    return _PLATFORM_SETTINGS


@router.delete("/settings/research-domains/{name}")
def remove_research_domain(
    name: str,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
):
    if name in _PLATFORM_SETTINGS["research_domains"]:
        _PLATFORM_SETTINGS["research_domains"].remove(name)
    return _PLATFORM_SETTINGS
