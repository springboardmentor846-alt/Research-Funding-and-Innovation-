"""Patent sync engine.

The orchestrator that runs the patent providers, hands their batches
to ``PatentIngestService``, and persists run-level metrics.  Mirrors
``app.funding_intel.services.sync.SyncEngine`` so the platform has a
single, familiar pattern for both services.
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.db import SessionLocal
from app.models.patent import Patent
from app.patents.core.config import patent_intel_settings, provider_flags
from app.patents.core.registry import (
    all_patent_providers,
    enabled_patent_provider_names,
    get_patent_provider,
    known_patent_providers,
)
from app.patents.models import PatentSyncControl, PatentSyncRun
from app.patents.services.ingest import PatentIngestService, IngestReport


@dataclass
class PatentProviderReport:
    """Per-provider outcome of a sync run."""

    provider: str
    status: str  # success | failed | skipped | disabled
    started_at: datetime
    finished_at: Optional[datetime]
    records_fetched: int
    records_inserted: int
    records_updated: int
    records_skipped: int
    duplicates_removed: int
    duration_ms: Optional[float]
    error_message: Optional[str]


class PatentSyncEngine:
    """The single entry point used by both the API and the scheduler."""

    def __init__(self, db: Optional[Session] = None) -> None:
        self.db = db or SessionLocal()
        self._owns_session = db is None

    async def run(
        self,
        *,
        provider: Optional[str] = None,
        mode: str = "incremental",
        force: bool = False,
    ) -> Dict:
        """Run a patent sync; return a JSON-serialisable summary."""
        s = patent_intel_settings

        if not force and not s.ENABLED:
            return {
                "status": "skipped",
                "message": "Patent Intelligence Service is disabled (set ENABLED=true)",
                "providers": [],
            }

        if not force:
            control = self.db.query(PatentSyncControl).first()
            if control and control.is_paused:
                return {
                    "status": "paused",
                    "message": "Patent sync paused by administrator",
                    "providers": [],
                }

        targets = self._resolve_providers(provider)
        if not targets:
            return {
                "status": "skipped",
                "message": "No enabled patent providers match the request",
                "providers": [],
            }

        run = PatentSyncRun(provider=provider, mode=mode, status="running")
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        started_at = datetime.utcnow()
        all_reports: List[Dict] = []
        aggregated = IngestReport()

        for prov in targets:
            report = await self._run_provider(prov, mode=mode, run_id=run.id)
            all_reports.append(report)
            aggregated.merge(
                IngestReport(
                    fetched=report["records_fetched"],
                    inserted=report["records_inserted"],
                    updated=report["records_updated"],
                    skipped=report["records_skipped"],
                    duplicates_removed=report["duplicates_removed"],
                )
            )

        finished_at = datetime.utcnow()
        any_failed = any(r["status"] == "failed" for r in all_reports)
        run.status = "failed" if any_failed else "success"
        run.started_at = started_at
        run.finished_at = finished_at
        run.records_fetched = aggregated.fetched
        run.records_inserted = aggregated.inserted
        run.records_updated = aggregated.updated
        run.records_skipped = aggregated.skipped
        run.duplicates_removed = aggregated.duplicates_removed
        if any_failed:
            failed = [r for r in all_reports if r["status"] == "failed"]
            run.error_message = "; ".join(
                f"{r['provider']}: {r.get('error_message', 'unknown')}" for r in failed
            )[:1000]
        self.db.commit()

        # Fire a patent-intelligence alert for every active user when a
        # sync adds new relevant patents.  Best-effort: a notification
        # write failure must never break the sync pipeline.
        if aggregated.inserted > 0:
            try:
                from app.models.user import User
                from app.services.notification_service import (
                    notify_patent_intel_update,
                )
                session = SessionLocal()
                try:
                    users = (
                        session.query(User).filter(User.is_active.is_(True)).all()
                    )
                    for u in users:
                        notify_patent_intel_update(
                            user=u,
                            relevant_patent_count=int(aggregated.inserted),
                            db=session,
                        )
                finally:
                    session.close()
            except Exception as exc:  # pragma: no cover
                logger.warning(
                    f"patent notification hook failed: {exc}"
                )

        return {
            "status": run.status,
            "mode": mode,
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "providers": all_reports,
            "totals": {
                "fetched": aggregated.fetched,
                "inserted": aggregated.inserted,
                "updated": aggregated.updated,
                "skipped": aggregated.skipped,
                "duplicates_removed": aggregated.duplicates_removed,
            },
            "run_id": run.id,
        }

    async def _run_provider(self, prov_name: str, *, mode: str, run_id: int) -> Dict:
        provider = get_patent_provider(prov_name)
        if provider is None:
            return {
                "provider": prov_name,
                "status": "skipped",
                "started_at": datetime.utcnow().isoformat(),
                "finished_at": datetime.utcnow().isoformat(),
                "records_fetched": 0,
                "records_inserted": 0,
                "records_updated": 0,
                "records_skipped": 0,
                "duplicates_removed": 0,
                "duration_ms": 0.0,
                "error_message": "unknown provider",
            }

        if not provider.health().enabled:
            return {
                "provider": prov_name,
                "status": "disabled",
                "started_at": datetime.utcnow().isoformat(),
                "finished_at": datetime.utcnow().isoformat(),
                "records_fetched": 0,
                "records_inserted": 0,
                "records_updated": 0,
                "records_skipped": 0,
                "duplicates_removed": 0,
                "duration_ms": 0.0,
                "error_message": None,
            }

        started = time.perf_counter()
        started_at = datetime.utcnow()
        try:
            await provider.initialize()
            cursor: Optional[str] = None
            ingest = PatentIngestService(self.db)
            per_provider = IngestReport()
            page = 0
            max_pages = patent_intel_settings.SYNC_MAX_PAGES_PER_RUN
            # Compute the incremental cursor once per run: the most
            # recent ``last_synced_at`` in the patents table (or
            # ``None`` to fall back to the provider's default).  We
            # use the engine session so the read sees the just-
            # committed rows from this very run.
            since = None
            if mode == "incremental":
                since = (
                    self.db.query(func.max(Patent.last_synced_at))
                    .scalar()
                )
                if since is not None and hasattr(since, "isoformat"):
                    since = since.isoformat()
            while page < max_pages:
                batch = await provider.fetch_batch(
                    cursor=cursor, mode=mode, since=since
                )
                normalized = []
                for raw in batch.records:
                    try:
                        norm = provider.normalize(raw)
                    except Exception as exc:
                        per_provider.errors.append(
                            {"record_id": str(raw.get("source_id") or raw.get("id")),
                             "message": f"normalize failed: {exc}"}
                        )
                        continue
                    if norm is None:
                        per_provider.skipped += 1
                        continue
                    normalized.append(norm)
                if normalized:
                    rep = ingest.ingest(normalized)
                    per_provider.merge(rep)
                cursor = batch.next_cursor
                page += 1
                if not cursor:
                    break
            await provider.aclose()
            elapsed = (time.perf_counter() - started) * 1000.0
            return {
                "provider": prov_name,
                "status": "success",
                "started_at": started_at.isoformat(),
                "finished_at": datetime.utcnow().isoformat(),
                "records_fetched": per_provider.fetched,
                "records_inserted": per_provider.inserted,
                "records_updated": per_provider.updated,
                "records_skipped": per_provider.skipped,
                "duplicates_removed": per_provider.duplicates_removed,
                "duration_ms": elapsed,
                "error_message": None,
            }
        except Exception as exc:
            logger.exception(f"[patent-sync] {prov_name} failed: {exc}")
            elapsed = (time.perf_counter() - started) * 1000.0
            try:
                await provider.aclose()
            except Exception:
                pass
            return {
                "provider": prov_name,
                "status": "failed",
                "started_at": started_at.isoformat(),
                "finished_at": datetime.utcnow().isoformat(),
                "records_fetched": 0,
                "records_inserted": 0,
                "records_updated": 0,
                "records_skipped": 0,
                "duplicates_removed": 0,
                "duration_ms": elapsed,
                "error_message": str(exc)[:500],
            }

    # ------------------------------------------------------------------
    def _resolve_providers(self, provider: Optional[str]) -> List[str]:
        if provider:
            flags = provider_flags()
            if not flags.get(provider, False):
                return []
            return [provider]
        return enabled_patent_provider_names()
