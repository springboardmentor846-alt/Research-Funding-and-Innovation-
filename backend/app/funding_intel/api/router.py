"""Admin-facing FastAPI router for the Funding Intelligence Service.

Mounted by ``app.main`` under ``/api/v1/funding-intel``. Every endpoint
requires the admin role — these are platform-management surfaces, not
public endpoints. The admin never creates funding opportunities
through this UI; they only trigger syncs and inspect outcomes.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.v1.deps import require_role
from app.core.logging import logger
from app.db import get_db
from app.funding_intel.core.config import funding_intel_settings, provider_flags
from app.funding_intel.core.registry import all_providers, enabled_provider_names, known_providers
from app.funding_intel.models import FundingSource, SyncControl, SyncRun, SyncRunError
from app.funding_intel.schemas.unified import (
    FailedRecordResponse,
    FundingIntelDashboardResponse,
    ProviderHealthResponse,
    SyncLogResponse,
    SyncRunResponse,
)
from app.funding_intel.services.sync import SyncEngine
from app.models.funding import Funding
from app.models.user import User, UserRole


router = APIRouter(prefix="/funding-intel", tags=["Funding Intelligence"])


# Track in-flight runs to avoid double-triggering from the UI.
_RUN_LOCKS: Dict[str, asyncio.Lock] = {}


def _lock_for(provider: Optional[str]) -> asyncio.Lock:
    key = provider or "all"
    if key not in _RUN_LOCKS:
        _RUN_LOCKS[key] = asyncio.Lock()
    return _RUN_LOCKS[key]


# ---------------------------------------------------------------------------
# Sync control
# ---------------------------------------------------------------------------
@router.post("/sync", response_model=SyncRunResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_sync(
    payload: Optional[Dict[str, Any]] = None,
    background_tasks: BackgroundTasks = None,  # type: ignore[assignment]
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Trigger a sync. Optional body: ``{"provider": "nih", "mode": "incremental", "force": false}``.

    Runs synchronously so the admin can see immediate results, but the
    call returns as soon as the provider run completes for that single
    provider. For multi-provider syncs the engine runs them sequentially.
    """
    payload = payload or {}
    provider = payload.get("provider")
    mode = payload.get("mode", "incremental")
    force = bool(payload.get("force", False))
    if mode not in ("incremental", "full"):
        raise HTTPException(status_code=400, detail="mode must be 'incremental' or 'full'")

    flags = provider_flags()
    s = funding_intel_settings
    if not force and not s.ENABLED:
        raise HTTPException(status_code=409, detail="Funding Intelligence Service is disabled")

    if not force:
        control = db.query(SyncControl).first()
        if control and control.is_paused:
            raise HTTPException(status_code=409, detail="Sync is paused by administrator")

    engine = SyncEngine(db=db)
    try:
        result = await engine.run(provider=provider, mode=mode, force=force)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover - safety net
        logger.exception(f"sync failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

    # Build a SyncRunResponse from the latest row.
    latest = (
        db.query(SyncRun)
        .filter(SyncRun.provider.in_([r["provider"] for r in result.get("providers", [])]))
        .order_by(SyncRun.started_at.desc())
        .first()
    )
    if latest is None:
        # No providers ran — return a synthetic summary.
        return SyncRunResponse(
            run_id=0,
            provider=provider,
            mode=mode,
            started_at=datetime.utcnow(),
            finished_at=datetime.utcnow(),
            duration_ms=0.0,
            status=result.get("status", "skipped"),
            records_fetched=0,
            records_inserted=0,
            records_updated=0,
            records_skipped=0,
            duplicates_removed=0,
            expired_marked=0,
            errors=[],
            message=result.get("message"),
        )
    return _serialize_run(latest)


@router.post("/sync/pause")
def pause_sync(
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Pause scheduled syncs (manual sync with ``force=true`` still works)."""
    control = db.query(SyncControl).first()
    if control is None:
        control = SyncControl(id=1, is_paused=True)
        db.add(control)
    else:
        control.is_paused = True
    control.updated_at = datetime.utcnow()
    db.commit()
    return {"paused": True, "updated_at": control.updated_at.isoformat()}


@router.post("/sync/resume")
def resume_sync(
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    control = db.query(SyncControl).first()
    if control is None:
        control = SyncControl(id=1, is_paused=False)
        db.add(control)
    else:
        control.is_paused = False
    control.updated_at = datetime.utcnow()
    db.commit()
    return {"paused": False, "updated_at": control.updated_at.isoformat()}


# ---------------------------------------------------------------------------
# Observability
# ---------------------------------------------------------------------------
@router.get("/dashboard", response_model=FundingIntelDashboardResponse)
async def intel_dashboard(
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Aggregated KPIs for the admin Funding Intelligence page."""
    s = funding_intel_settings
    flags = provider_flags()
    enabled = [n for n in flags if flags[n]]

    health = await SyncEngine(db=db).health()
    providers: List[ProviderHealthResponse] = [
        ProviderHealthResponse(**p) for p in health.get("providers", [])
    ]

    control = db.query(SyncControl).first()
    last_sync = db.query(SyncRun).order_by(SyncRun.started_at.desc()).first()
    last_sync_at = last_sync.started_at if last_sync else None

    funding_total = db.query(func.count(Funding.id)).scalar() or 0
    funding_active = (
        db.query(func.count(Funding.id)).filter(Funding.is_active == True).scalar() or 0  # noqa: E712
    )

    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    funding_imported_today = (
        db.query(func.count(Funding.id))
        .filter(Funding.created_at >= today_start)
        .scalar() or 0
    )
    funding_updated_today = (
        db.query(func.count(SyncRun.id))
        .filter(SyncRun.started_at >= today_start, SyncRun.records_updated > 0)
        .scalar() or 0
    )
    duplicates_removed_today = (
        db.query(func.coalesce(func.sum(SyncRun.duplicates_removed), 0))
        .filter(SyncRun.started_at >= today_start)
        .scalar() or 0
    )
    expired_today = (
        db.query(func.coalesce(func.sum(SyncRun.expired_marked), 0))
        .filter(SyncRun.started_at >= today_start)
        .scalar() or 0
    )

    recent_runs = (
        db.query(SyncRun)
        .order_by(SyncRun.started_at.desc())
        .limit(5)
        .all()
    )

    # Average response time over the last 10 runs.
    recent_for_avg = (
        db.query(SyncRun.avg_response_ms)
        .filter(SyncRun.avg_response_ms.isnot(None))
        .order_by(SyncRun.started_at.desc())
        .limit(10)
        .all()
    )
    avg_rt = None
    if recent_for_avg:
        vals = [r[0] for r in recent_for_avg if r[0] is not None]
        if vals:
            avg_rt = sum(vals) / len(vals)

    recent_runs_dto = [_serialize_run(r) for r in recent_runs]
    # Compute error rate over last 24h.
    cutoff = datetime.utcnow() - timedelta(hours=24)
    total_24h = db.query(func.count(SyncRun.id)).filter(SyncRun.started_at >= cutoff).scalar() or 0
    failed_24h = (
        db.query(func.count(SyncRun.id))
        .filter(SyncRun.started_at >= cutoff, SyncRun.status == "failed")
        .scalar() or 0
    )
    error_rate_pct = (failed_24h / total_24h * 100.0) if total_24h else 0.0

    return FundingIntelDashboardResponse(
        apis_connected=len(health.get("connected", [])),
        apis_enabled=len(enabled),
        apis_healthy=sum(1 for p in providers if p.status == "healthy"),
        apis_degraded=sum(1 for p in providers if p.status == "degraded"),
        apis_error=sum(1 for p in providers if p.status == "error"),
        sync_status=_sync_status(db),
        last_sync_at=last_sync_at,
        next_sync_at=control.next_scheduled_sync_at if control else None,
        funding_total=int(funding_total),
        funding_active=int(funding_active),
        funding_imported_today=int(funding_imported_today),
        funding_updated_today=int(funding_updated_today),
        duplicates_removed_today=int(duplicates_removed_today),
        expired_today=int(expired_today),
        avg_response_time_ms=round(avg_rt, 2) if avg_rt else None,
        error_rate_pct=round(error_rate_pct, 2),
        providers=providers,
        recent_runs=recent_runs_dto,
    )


@router.get("/providers", response_model=List[ProviderHealthResponse])
async def list_providers(
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    health = await SyncEngine(db=db).health()
    return [ProviderHealthResponse(**p) for p in health.get("providers", [])]


@router.get("/logs", response_model=SyncLogResponse)
def list_sync_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    provider: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Paginated history of sync runs."""
    query = db.query(SyncRun)
    if provider:
        query = query.filter(SyncRun.provider == provider)
    if status_filter:
        query = query.filter(SyncRun.status == status_filter)

    total = query.count()
    items = (
        query.order_by(SyncRun.started_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    total_pages = (total + page_size - 1) // page_size if total else 0
    return SyncLogResponse(
        items=[_serialize_run(i).model_dump() for i in items],
        total=int(total),
        page=page,
        page_size=page_size,
        total_pages=int(total_pages),
    )


@router.get("/logs/{run_id}")
def get_sync_log(
    run_id: int,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    run = db.query(SyncRun).filter(SyncRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    out = _serialize_run(run).model_dump()
    out["errors"] = [
        {
            "id": e.id,
            "source_id": e.source_id,
            "error_type": e.error_type,
            "error_message": e.error_message,
            "occurred_at": e.occurred_at.isoformat() if e.occurred_at else None,
        }
        for e in run.errors
    ]
    return out


@router.get("/failed-records", response_model=FailedRecordResponse)
def list_failed_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    provider: Optional[str] = None,
    error_type: Optional[str] = None,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Paginated view of per-record errors captured during sync."""
    query = db.query(SyncRunError)
    if provider:
        query = query.filter(SyncRunError.provider == provider)
    if error_type:
        query = query.filter(SyncRunError.error_type == error_type)

    total = query.count()
    items = (
        query.order_by(SyncRunError.occurred_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    total_pages = (total + page_size - 1) // page_size if total else 0
    return FailedRecordResponse(
        items=[
            {
                "id": e.id,
                "run_id": e.run_id,
                "provider": e.provider,
                "source_id": e.source_id,
                "error_type": e.error_type,
                "error_message": e.error_message,
                "occurred_at": e.occurred_at.isoformat() if e.occurred_at else None,
            }
            for e in items
        ],
        total=int(total),
        page=page,
        page_size=page_size,
        total_pages=int(total_pages),
    )


# ---------------------------------------------------------------------------
# Read-only funding data (for the admin "Imported Funding" view)
# ---------------------------------------------------------------------------
@router.get("/funding")
def list_imported_funding(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    search: Optional[str] = None,
    source: Optional[str] = None,
    domain: Optional[str] = None,
    country: Optional[str] = None,
    is_active: Optional[bool] = None,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Read-only view of funding imported via the Funding Intelligence Service."""
    from sqlalchemy import or_

    query = db.query(Funding)
    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                Funding.title.ilike(term),
                Funding.description.ilike(term),
                Funding.keywords.ilike(term),
                Funding.organization.ilike(term),
            )
        )
    if domain:
        query = query.filter(Funding.research_domain == domain)
    if country:
        query = query.filter(Funding.country == country)
    if is_active is not None:
        query = query.filter(Funding.is_active == is_active)
    if source:
        query = query.join(Funding.sources).filter(FundingSource.source == source).distinct()

    total = query.count()
    items = (
        query.order_by(Funding.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    total_pages = (total + page_size - 1) // page_size if total else 0
    return {
        "items": [
            {
                "id": f.id,
                "title": f.title,
                "description": (f.description or "")[:600],
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
                "updated_at": f.updated_at.isoformat() if f.updated_at else None,
                "sources": [
                    {"source": s.source, "source_id": s.source_id, "last_synced_at": s.last_synced_at.isoformat() if s.last_synced_at else None}
                    for s in (f.sources or [])
                ],
            }
            for f in items
        ],
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "total_pages": int(total_pages),
    }


@router.get("/funding/stats")
def funding_intel_stats(
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Compact stats tile data for the admin Funding page."""
    total = db.query(func.count(Funding.id)).scalar() or 0
    active = (
        db.query(func.count(Funding.id)).filter(Funding.is_active == True).scalar() or 0  # noqa: E712
    )
    by_source: Dict[str, int] = {}
    for row in db.query(FundingSource.source, func.count(FundingSource.id)).group_by(FundingSource.source).all():
        by_source[row[0]] = int(row[1])
    by_country: Dict[str, int] = {}
    rows = db.query(Funding.country, func.count(Funding.id)).group_by(Funding.country).all()
    for row in rows:
        by_country[row[0] or "International"] = int(row[1])
    by_domain: Dict[str, int] = {}
    rows = db.query(Funding.research_domain, func.count(Funding.id)).group_by(Funding.research_domain).all()
    for row in rows:
        by_domain[row[0] or "Unspecified"] = int(row[1])
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    imported_today = (
        db.query(func.count(Funding.id)).filter(Funding.created_at >= today_start).scalar() or 0
    )
    updated_today = (
        db.query(func.count(Funding.id)).filter(Funding.updated_at >= today_start).scalar() or 0
    )
    return {
        "total_funding": int(total),
        "active_funding": int(active),
        "by_source": [{"source": k, "count": v} for k, v in sorted(by_source.items(), key=lambda x: -x[1])],
        "by_country": [{"country": k, "count": v} for k, v in sorted(by_country.items(), key=lambda x: -x[1])],
        "by_domain": [{"domain": k, "count": v} for k, v in sorted(by_domain.items(), key=lambda x: -x[1])],
        "imported_today": int(imported_today),
        "updated_today": int(updated_today),
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _serialize_run(run: SyncRun) -> SyncRunResponse:
    return SyncRunResponse(
        run_id=run.id,
        provider=run.provider,
        mode=run.mode,
        started_at=run.started_at,
        finished_at=run.finished_at,
        duration_ms=run.duration_ms,
        status=run.status,
        records_fetched=run.records_fetched,
        records_inserted=run.records_inserted,
        records_updated=run.records_updated,
        records_skipped=run.records_skipped,
        duplicates_removed=run.duplicates_removed,
        expired_marked=run.expired_marked,
        errors=(run.error_message.split("\n") if run.error_message else []),
        message=None,
    )


def _sync_status(db: Session) -> str:
    """Aggregate sync status string for the admin dashboard."""
    last = db.query(SyncRun).order_by(SyncRun.started_at.desc()).first()
    control = db.query(SyncControl).first()
    if control and control.is_paused:
        return "paused"
    if last is None:
        return "idle"
    if last.status == "running":
        return "running"
    if last.status == "failed":
        return "error"
    return "idle"
