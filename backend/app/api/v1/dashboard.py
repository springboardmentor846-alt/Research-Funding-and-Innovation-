"""Dashboard analytics endpoints.

All dashboard values are computed live from the database (and the AI
recommender) by :mod:`app.utils.dashboard_metrics`. This endpoint
returns the spec-defined flat shape:

    {
        "publications": ...,
        "citations": ...,
        "h_index": ...,
        "i10_index": ...,
        "innovation_score": ...,
        "commercialization_score": ...,
        "available_funding": ...,
        "productivity": ...
    }

The endpoint keeps returning the rest of the data the dashboard UI
already consumes (charts, funding landscape, trending keywords, user
header) so the frontend upgrade can be incremental.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.publication import Publication
from app.models.funding import Funding
from app.models.user import User
from app.api.v1.deps import get_current_user
from app.services.publication_service import PublicationService
from app.services.funding_service import FundingService
from app.services.saved_patent_service import SavedPatentService
from app.ai.trends import trend_analyzer
from app.utils import dashboard_metrics

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview")
def dashboard_overview(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Top-level dashboard data for the current user.

    Returns the spec-defined flat metrics block in ``metrics`` plus the
    legacy structures the dashboard UI still consumes. The metrics
    block is the source of truth for the eight KPI cards; nothing in
    this response is hardcoded.
    """
    pubs = current.publications

    # Publication aggregates — single round trip; citation_counts list
    # feeds both the H-index and the i10-index helpers.
    total_publications, total_citations, citation_counts = (
        dashboard_metrics.load_publication_aggregates(db, current.id)
    )
    computed_h_index = dashboard_metrics.h_index(citation_counts)
    computed_i10 = dashboard_metrics.i10_index(citation_counts)
    computed_productivity = dashboard_metrics.productivity(
        total_citations, total_publications
    )

    # Patents attributable to the user.
    patent_count = dashboard_metrics.load_patent_count_for_user(db, current)

    # Saved-patents bookmark count — distinct from the ILIKE-based
    # portfolio heuristic above; this is the explicit user library.
    saved_patents_count = SavedPatentService.count_for_user(db, current.id)

    # Innovation & commercialization scores.
    innovation = dashboard_metrics.innovation_score(
        publications=total_publications,
        citations=total_citations,
        h_index_value=computed_h_index,
        patents=patent_count,
    )

    # Industry data — best-effort. Each bucket has a presence flag so
    # the adaptive commercialization formula can re-normalise the
    # remaining weights if some data sources are empty.
    industry_collabs = dashboard_metrics.load_industry_collaborations(db, current.id)
    tech_transfers = dashboard_metrics.load_technology_transfers(db, current.id)
    licenses = dashboard_metrics.load_licenses(db, current.id)
    startups = dashboard_metrics.load_startups(db, current.id)
    industry_projects = dashboard_metrics.load_industry_funded_projects(
        db, current.id
    )
    # Presence flags — derived from whether the corresponding query
    # returned any rows. If the query is empty (data source is empty
    # for this user) we drop that bucket from the weighted sum and
    # re-normalise.
    has_industry_data = bool(industry_collabs) or bool(industry_projects)
    has_tech_transfers = bool(tech_transfers)
    has_licenses = bool(licenses)
    has_startups = bool(startups)
    has_patents = bool(patent_count)
    commercial = dashboard_metrics.commercialization_score_adaptive(
        patents=patent_count,
        industry_collaborations=len(industry_collabs) + industry_projects,
        technology_transfers=tech_transfers,
        licenses=licenses,
        startups=startups,
        patents_present=has_patents,
        industry_collaborations_present=has_industry_data,
        technology_transfers_present=has_tech_transfers,
        licenses_present=has_licenses,
        startups_present=has_startups,
    )

    # Available funding — opportunities matching the user with AI
    # match score >= 70%. The helper itself never raises (it logs and
    # returns 0 on every failure path). We log here too so a regression
    # in the helper is visible in the application logs instead of being
    # silently swallowed by a bare ``except``.
    try:
        available_funding = dashboard_metrics.available_funding_count(db, current)
    except Exception as exc:  # pragma: no cover - last-resort guard
        from app.core.logging import logger
        logger.exception(f"[dashboard] available_funding_count crashed: {exc}")
        available_funding = 0

    # Legacy trend / chart data (unchanged so the existing dashboard
    # charts keep working).
    pub_stats = PublicationService.get_stats(db, current.id)
    funding_stats = FundingService.get_stats(db)
    keywords = trend_analyzer.extract_trending_keywords(pubs, top_n=10)
    citation_trends = trend_analyzer.citation_trends(pubs)
    domain_dist = trend_analyzer.domain_distribution(pubs)
    research_growth = trend_analyzer.research_growth(pubs)
    tech_evolution = trend_analyzer.technology_evolution(pubs)

    return {
        # ---- Spec-defined flat metrics (consumed by the 8 KPI cards) ----
        "metrics": {
            "publications": int(total_publications),
            "citations": int(total_citations),
            "h_index": int(computed_h_index),
            "i10_index": int(computed_i10),
            "innovation_score": int(innovation),
            "commercialization_score": int(commercial),
            "available_funding": int(available_funding),
            "productivity": float(computed_productivity),
            "saved_patents_count": int(saved_patents_count),
        },
        # ---- Backwards-compatible fields used by the rest of the UI ----
        "user": {
            "name": current.full_name or current.username,
            "role": current.role.value,
            # h_index / i10_index are now computed live; expose them at
            # the user level too so existing chart code keeps working.
            "h_index": int(computed_h_index),
            "i10_index": int(computed_i10),
            "citation_count": int(total_citations),
        },
        "kpis": {
            "total_publications": int(total_publications),
            "total_citations": int(total_citations),
            "innovation_score": int(innovation),
            "commercialization_score": int(commercial),
            "research_productivity": float(computed_productivity),
            "available_funding": int(available_funding),
            "saved_patents_count": int(saved_patents_count),
        },
        "trending_keywords": keywords,
        "citation_trends": citation_trends,
        "domain_distribution": domain_dist,
        "research_growth": research_growth,
        "technology_evolution": tech_evolution,
        "funding_overview": {
            "total": funding_stats["total_funding"],
            "active": funding_stats["active_funding"],
            "by_type": funding_stats["by_type"],
            "by_domain": funding_stats["by_domain"],
        },
    }


@router.get("/platform")
def platform_dashboard(
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Platform-wide analytics (for innovation managers & admins)."""
    from sqlalchemy import func

    total_publications = db.query(func.count(Publication.id)).scalar() or 0
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_funding = db.query(func.count(Funding.id)).scalar() or 0
    total_citations = (
        db.query(func.coalesce(func.sum(Publication.citation_count), 0)).scalar() or 0
    )
    return {
        "total_publications": total_publications,
        "total_users": total_users,
        "total_funding": total_funding,
        "total_citations": int(total_citations),
    }
