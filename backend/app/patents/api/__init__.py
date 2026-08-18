"""Patent Intelligence REST API (Milestone 3).

All endpoints live under ``/api/v1/patents/intel/*`` and are mounted
in ``app.main`` alongside the existing ``/api/v1/patents/*`` routes.

The router never returns hardcoded numbers — every value is computed
from the ``patents`` table by the underlying services.  The ``/search``
endpoint is the one exception: it transparently proxies a live Lens
Patent API query for the duration of one request, returning the raw
upstream records so the UI can render snippets before they are
materialised into the database.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.api.v1.deps import get_current_user
from app.core.logging import logger
from app.db import get_db
from app.models.user import User
from app.patents.core.config import patent_intel_settings, provider_flags
from app.patents.providers.lens_client import (
    LensAuthError,
    LensError,
    LensRateLimitError,
    LensSearchFilters,
)
from app.patents.services.commercialization_service import CommercializationService
from app.patents.services.dashboard_service import PatentDashboardService
from app.patents.services.innovation_scoring_service import InnovationScoringService
from app.patents.services.landscape_service import PatentLandscapeService
from app.patents.services.sync import PatentSyncEngine
from app.patents.services.technology_intel_service import TechnologyIntelligenceService


router = APIRouter(prefix="/patents/intel", tags=["Patent Intelligence"])


# ---------------------------------------------------------------------------
# Patent Landscape Analysis
# ---------------------------------------------------------------------------
@router.get("/landscape")
def patent_landscape(
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Patent landscape analysis derived from the live corpus."""
    return PatentLandscapeService(db).overview()


# ---------------------------------------------------------------------------
# Technology Intelligence
# ---------------------------------------------------------------------------
@router.get("/clusters")
def technology_clusters(
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """K-Means clusters of semantically similar patents."""
    return TechnologyIntelligenceService(db).cluster_patents()


@router.get("/emerging")
def emerging_technologies(
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Emerging technologies in the corpus."""
    return TechnologyIntelligenceService(db).emerging_technologies()


@router.get("/fast-growing")
def fast_growing_technologies(
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fast-growing technologies in the corpus."""
    return TechnologyIntelligenceService(db).fast_growing_technologies()


@router.get("/highly-cited")
def highly_cited_patents(
    limit: int = Query(10, ge=1, le=50),
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Top-cited patents in the corpus."""
    return TechnologyIntelligenceService(db).highly_cited_patents(limit=limit)


@router.get("/similar/{patent_id}")
def similar_patents(
    patent_id: int,
    top_k: int = Query(5, ge=1, le=20),
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Patents semantically similar to the given patent_id."""
    return TechnologyIntelligenceService(db).similar_patents(patent_id, top_k=top_k)


# ---------------------------------------------------------------------------
# Innovation Scoring
# ---------------------------------------------------------------------------
@router.post("/scores/recompute")
def recompute_scores(
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Recompute innovation scores for the entire corpus."""
    return InnovationScoringService(db).compute_all()


@router.get("/scores/{patent_id}")
def patent_innovation_score(
    patent_id: int,
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Innovation score breakdown for a single patent."""
    score = InnovationScoringService(db).score_for_patent(patent_id)
    if score is None:
        raise HTTPException(status_code=404, detail="Patent not found")
    return score


# ---------------------------------------------------------------------------
# Commercialization
# ---------------------------------------------------------------------------
@router.post("/recommendations/recompute")
def recompute_recommendations(
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Recompute commercialization labels for every patent."""
    return CommercializationService(db).compute_for_all()


@router.get("/recommendations")
def commercialization_recommendations(
    limit: int = Query(10, ge=1, le=50),
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Top commercialization recommendations ranked by innovation score."""
    return CommercializationService(db).top_recommendations(limit=limit)


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@router.get("/dashboard")
def patent_dashboard(
    force_refresh: bool = Query(False),
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Full Patent Analytics & Innovation Intelligence dashboard.

    Cached for 5 minutes; pass ``?force_refresh=true`` to bypass the
    cache and recompute every signal.
    """
    return PatentDashboardService(db).get_dashboard(force_refresh=force_refresh)


@router.post("/dashboard/refresh")
def patent_dashboard_refresh(
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Force a full dashboard refresh."""
    return PatentDashboardService(db).refresh()


# ---------------------------------------------------------------------------
# Sync
# ---------------------------------------------------------------------------
@router.get("/sync/status")
def patent_sync_status(
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the latest patent sync run."""
    from app.patents.models import PatentSyncRun
    run = (
        db.query(PatentSyncRun)
        .order_by(PatentSyncRun.id.desc())
        .first()
    )
    if run is None:
        return {"status": "never_run"}
    return run.to_dict()


@router.post("/sync")
async def patent_sync(
    payload: Optional[dict] = None,
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger a manual patent sync.

    Body (all optional):
      ``{"provider": "the_lens", "mode": "incremental", "force": false}``
    """
    payload = payload or {}
    provider = payload.get("provider")
    mode = payload.get("mode", "incremental")
    force = bool(payload.get("force", False))
    if mode not in ("incremental", "full"):
        raise HTTPException(status_code=400, detail="mode must be 'incremental' or 'full'")
    engine = PatentSyncEngine(db=db)
    try:
        result = await engine.run(provider=provider, mode=mode, force=force)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))
    return result


# ---------------------------------------------------------------------------
# Live Lens proxy (read-only)
# ---------------------------------------------------------------------------
@router.get("/search")
async def patent_search(
    q: Optional[str] = Query(None, description="Keyword/phrase to match (Lens free_text)."),
    inventor: Optional[str] = Query(None, description="Inventor display name (exact-ish match)."),
    assignee: Optional[str] = Query(None, description="Assignee/applicant display name."),
    cpc: Optional[str] = Query(None, description="CPC prefix to filter by, e.g. G06N."),
    ipc: Optional[str] = Query(None, description="IPC prefix to filter by."),
    country: Optional[str] = Query(None, description="Two-letter jurisdiction code, e.g. US."),
    year_from: Optional[int] = Query(None, ge=1900, le=2100),
    year_to: Optional[int] = Query(None, ge=1900, le=2100),
    size: int = Query(20, ge=1, le=100),
    from_offset: int = Query(0, ge=0, le=10_000),
    _current: User = Depends(get_current_user),
):
    """Proxy a live Lens Patent API search.

    The endpoint is read-only and never persists the results — it is
    meant for the "explore" UI where the user wants to see what the
    upstream has before triggering a sync.  Errors from the upstream
    are translated into HTTP 4xx/5xx responses with a descriptive
    detail message.
    """
    if not provider_flags().get("the_lens", False):
        raise HTTPException(
            status_code=503,
            detail="The Lens provider is not enabled (set THE_LENS_ENABLED=true)",
        )
    if not patent_intel_settings.LENS_API_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="LENS_API_TOKEN is not configured",
        )

    from app.patents.providers.the_lens import TheLensProvider

    provider = TheLensProvider()
    try:
        await provider.initialize()
        # Build the filter list from the optional parameters.
        filters = LensSearchFilters.combine(
            LensSearchFilters.keyword(q or ""),
            LensSearchFilters.inventor(inventor or ""),
            LensSearchFilters.assignee(assignee or ""),
            LensSearchFilters.technology_domain(cpc=cpc, ipc=ipc),
            LensSearchFilters.country(country or ""),
            LensSearchFilters.year_range(start=year_from, end=year_to),
        )
        result = await provider.search_by_keyword(
            q or "*", size=size, from_offset=from_offset
        )
        # Filter-only searches need a different entry-point.
        if inventor or assignee or cpc or ipc or country or year_from or year_to:
            result = await provider._client.search(  # type: ignore[attr-defined]
                query=q or "*",
                from_offset=from_offset,
                size=size,
                filters=filters or None,
            )
        return {
            "total": result.total,
            "from": from_offset,
            "size": size,
            "results": result.records,
        }
    except LensAuthError as exc:
        logger.warning(f"[patents/intel/search] auth error: {exc}")
        raise HTTPException(status_code=503, detail=f"Lens auth failed: {exc}")
    except LensRateLimitError as exc:
        raise HTTPException(status_code=429, detail=f"Lens rate-limited: {exc}")
    except LensError as exc:
        logger.exception(f"[patents/intel/search] lens error: {exc}")
        raise HTTPException(status_code=502, detail=f"Lens error: {exc}")
    finally:
        try:
            await provider.aclose()
        except Exception:
            pass


@router.get("/patent/{lens_id}")
async def patent_detail(
    lens_id: str,
    _current: User = Depends(get_current_user),
):
    """Fetch a single patent by Lens id from the upstream API."""
    if not provider_flags().get("the_lens", False):
        raise HTTPException(status_code=503, detail="The Lens provider is not enabled")
    if not patent_intel_settings.LENS_API_TOKEN:
        raise HTTPException(status_code=503, detail="LENS_API_TOKEN is not configured")

    from app.patents.providers.lens_client import LensNotFoundError
    from app.patents.providers.the_lens import TheLensProvider

    provider = TheLensProvider()
    try:
        await provider.initialize()
        record = await provider.fetch_patent(lens_id)
        return {"lens_id": lens_id, "record": record}
    except LensNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except LensAuthError as exc:
        raise HTTPException(status_code=503, detail=f"Lens auth failed: {exc}")
    except LensRateLimitError as exc:
        raise HTTPException(status_code=429, detail=f"Lens rate-limited: {exc}")
    except LensError as exc:
        logger.exception(f"[patents/intel/patent/{lens_id}] lens error: {exc}")
        raise HTTPException(status_code=502, detail=f"Lens error: {exc}")
    finally:
        try:
            await provider.aclose()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Sync control (pause / resume)
# ---------------------------------------------------------------------------
@router.post("/sync/pause")
def patent_sync_pause(
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Pause every scheduled and manual patent sync."""
    from app.patents.models import PatentSyncControl

    control = db.query(PatentSyncControl).first()
    if control is None:
        control = PatentSyncControl(is_paused=True)
        db.add(control)
    else:
        control.is_paused = True
        control.updated_at = None  # let the DB default take over
    db.commit()
    db.refresh(control)
    return {"is_paused": bool(control.is_paused)}


@router.post("/sync/resume")
def patent_sync_resume(
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Resume scheduled and manual patent sync."""
    from app.patents.models import PatentSyncControl

    control = db.query(PatentSyncControl).first()
    if control is None:
        control = PatentSyncControl(is_paused=False)
        db.add(control)
    else:
        control.is_paused = False
        control.updated_at = None
    db.commit()
    db.refresh(control)
    return {"is_paused": bool(control.is_paused)}


@router.get("/sync/control")
def patent_sync_control_status(
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the current pause/resume flag."""
    from app.patents.models import PatentSyncControl

    control = db.query(PatentSyncControl).first()
    return {
        "is_paused": bool(control.is_paused) if control else False,
        "updated_at": control.updated_at.isoformat() if control and control.updated_at else None,
    }
