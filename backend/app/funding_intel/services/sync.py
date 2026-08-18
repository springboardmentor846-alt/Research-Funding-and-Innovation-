"""High-level sync orchestrator.

This module owns the *flow* of a sync:

1. Resolve the set of providers to run.
2. For each provider:
   - Initialize its HTTP client.
   - Run ``fetch_batch`` until exhausted or ``SYNC_MAX_PAGES_PER_RUN`` reached.
   - Pass every raw record through ``normalize``.
   - Hand each ``NormalizedFunding`` to ``IngestService``.
3. Persist run-level metrics and update ``SyncControl``.

The orchestrator never raises — every provider's outcome is captured
in its ``ProviderRunResult`` and folded into the ``SyncRun`` row.
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.logging import logger
from app.db import SessionLocal
from app.funding_intel.core.config import funding_intel_settings, provider_flags
from app.funding_intel.core.registry import (
    all_providers,
    enabled_provider_names,
    get_provider,
    known_providers,
)
from app.funding_intel.models import SyncControl, SyncRun
from app.funding_intel.services.ingest import IngestService
from app.services.recommendation_service import RecommendationService


@dataclass
class ProviderReport:
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
    expired_marked: int
    duration_ms: Optional[float]
    error_message: Optional[str]


class SyncEngine:
    """The one entry point used by both the API and the scheduler."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()
        self._owns_session = db is None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def run(
        self,
        *,
        provider: Optional[str] = None,
        mode: str = "incremental",
        force: bool = False,
    ) -> Dict:
        """Run a sync; return a JSON-serialisable summary."""
        flags = provider_flags()
        s = funding_intel_settings

        if not force and not s.ENABLED:
            return {
                "status": "skipped",
                "message": "Funding Intelligence Service is disabled (set ENABLED=true)",
                "providers": [],
            }

        if not force:
            control = self.db.query(SyncControl).first()
            if control and control.is_paused:
                return {
                    "status": "paused",
                    "message": "Sync paused by administrator",
                    "providers": [],
                }

        targets = self._resolve_providers(provider)
        if not targets:
            return {
                "status": "skipped",
                "message": "No enabled providers match the request",
                "providers": [],
            }

        # ---- SPEC: "Synchronization Started" --------------------------------
        logger.info(
            f"[sync] Synchronization Started (mode={mode}, "
            f"providers={[p.name for p in targets]}, force={force})"
        )
        run_started_perf = time.perf_counter()
        run_started_at = datetime.utcnow()

        # Initialise every provider up-front (sync I/O setup only — no work yet).
        for prov in targets:
            try:
                await prov.initialize()
            except Exception as exc:
                logger.warning(f"[{prov.name}] initialize() failed: {exc}")
                prov._record_failure(str(exc))

        reports: List[ProviderReport] = []
        try:
            for prov in targets:
                if not flags.get(prov.name, False):
                    reports.append(
                        ProviderReport(
                            provider=prov.name,
                            status="disabled",
                            started_at=datetime.utcnow(),
                            finished_at=datetime.utcnow(),
                            records_fetched=0,
                            records_inserted=0,
                            records_updated=0,
                            records_skipped=0,
                            duplicates_removed=0,
                            expired_marked=0,
                            duration_ms=0.0,
                            error_message="provider disabled",
                        )
                    )
                    continue
                # ---- SPEC: "API Called" --------------------------------------
                logger.info(
                    f"[sync] API Called provider={prov.name} mode={mode}"
                )
                report = await self._run_one(prov, mode=mode)
                reports.append(report)
                # ---- SPEC: per-provider counters -----------------------------
                logger.info(
                    f"[sync] provider={prov.name} "
                    f"Records Received={report.records_fetched} "
                    f"Inserted={report.records_inserted} "
                    f"Updated={report.records_updated} "
                    f"Skipped={report.records_skipped} "
                    f"Duplicates={report.duplicates_removed} "
                    f"Expired={report.expired_marked} "
                    f"Duration={round(report.duration_ms or 0.0, 1)}ms"
                    + (f" Errors={len(report.error_message.splitlines()) if report.error_message else 0}"
                       if report.status != "success" else "")
                )
        finally:
            for prov in targets:
                try:
                    await prov.aclose()
                except Exception:  # pragma: no cover - shutdown best-effort
                    pass

        # Touch SyncControl (next-scheduled cursor).
        self._touch_control(mode=mode)

        # If anything was actually written, drop every user's cached
        # recommendations — the candidate set may have shifted for everyone.
        total_inserted = sum(r.records_inserted for r in reports)
        total_updated = sum(r.records_updated for r in reports)
        if total_inserted or total_updated:
            try:
                RecommendationService.invalidate_all(self.db)
            except Exception as exc:  # pragma: no cover - cache is best effort
                logger.warning(f"[sync] could not invalidate recommendation cache: {exc}")

        total_run_ms = round((time.perf_counter() - run_started_perf) * 1000.0, 1)
        status = (
            "success" if all(r.status in ("success", "disabled", "skipped") for r in reports) else "partial"
        )

        # ---- SPEC: "Synchronization Completed" ------------------------------
        logger.info(
            f"[sync] Synchronization Completed status={status} duration={total_run_ms}ms "
            f"started_at={run_started_at.isoformat()} finished_at={datetime.utcnow().isoformat()}"
        )

        return {
            "status": status,
            "mode": mode,
            "started_at": min(r.started_at for r in reports).isoformat(),
            "finished_at": max((r.finished_at or datetime.utcnow()) for r in reports).isoformat(),
            "providers": [self._report_to_dict(r) for r in reports],
        }

    async def health(self) -> Dict:
        """Return health snapshot for every registered provider."""
        providers = all_providers()
        for prov in providers:
            try:
                await prov.initialize()
            except Exception as exc:
                prov._record_failure(str(exc))
        try:
            snapshot = [prov.health().to_dict() for prov in providers]
        finally:
            for prov in providers:
                try:
                    await prov.aclose()
                except Exception:
                    pass
        return {
            "providers": snapshot,
            "enabled": [p.name for p in providers if p._health.enabled],
            "connected": [
                p.name for p in providers
                if p._health.enabled and p._health.consecutive_failures == 0
            ],
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _resolve_providers(self, provider_name: Optional[str]):
        if provider_name:
            prov = get_provider(provider_name)
            if prov is None:
                raise ValueError(f"unknown provider: {provider_name}")
            return [prov]
        # Use the registry's already-instantiated list so each call shares
        # the same configuration but separate HTTP clients.
        return all_providers()

    async def _run_one(self, provider, *, mode: str) -> ProviderReport:
        """Run a single provider end-to-end and record metrics."""
        s = funding_intel_settings
        started_at = datetime.utcnow()
        cursor = None if mode == "full" else None  # future: load last cursor per provider

        run = SyncRun(
            provider=provider.name,
            mode=mode,
            status="running",
            started_at=started_at,
            cursor_at_start=cursor,
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        ingest = IngestService(self.db, run)
        records_fetched = 0
        records_normalized = 0
        errors: List[str] = []
        started_perf = time.perf_counter()

        page_count = 0
        response_times: List[float] = []

        try:
            while page_count < s.SYNC_MAX_PAGES_PER_RUN:
                page_count += 1
                page_start = time.perf_counter()
                try:
                    batch = await provider.fetch_batch(
                        cursor=cursor, page_size=s.SYNC_PAGE_SIZE
                    )
                except Exception as exc:
                    err = f"fetch_batch failed: {exc}"
                    errors.append(err)
                    logger.error(f"[{provider.name}] {err}")
                    break

                response_times.append((time.perf_counter() - page_start) * 1000.0)

                raw_records = batch.records or []
                records_fetched += len(raw_records)
                logger.info(
                    f"[{provider.name}] Page {page_count} | "
                    f"Fetched={len(raw_records)} | "
                    f"Cursor={batch.next_cursor}"
                )
                normalized_records = []

                for raw in raw_records:
                    try:
                        normalized = provider.normalize(raw)
                    except Exception as exc:
                        errors.append(f"normalize failed: {exc}")
                        continue

                    if normalized is None:
                        ingest.stats.skipped += 1
                        continue

                    normalized_records.append(normalized)

                # One database commit per page instead of one per record
                if normalized_records:
                    ingest.ingest_batch(normalized_records)
                    records_normalized += len(normalized_records)

                # After ingestion, mark expired rows.
                expired = ingest.expire_stale()

                if batch.next_cursor is None:
                    break
                cursor = batch.next_cursor
        except Exception as exc:  # pragma: no cover - last-ditch
            errors.append(f"unexpected: {exc}")
            logger.exception(f"[{provider.name}] sync crashed: {exc}")
            expired = 0

        finished_at = datetime.utcnow()
        duration_ms = (time.perf_counter() - started_perf) * 1000.0

        run.finished_at = finished_at
        run.duration_ms = duration_ms
        run.records_fetched = records_fetched
        run.records_inserted = ingest.stats.inserted
        run.records_updated = ingest.stats.updated
        run.records_skipped = ingest.stats.skipped
        run.duplicates_removed = ingest.stats.duplicates
        run.expired_marked = expired or ingest.stats.expired
        run.cursor_at_end = cursor
        if response_times:
            run.avg_response_ms = sum(response_times) / len(response_times)
        run.status = "success" if not errors else ("partial" if (ingest.stats.inserted or ingest.stats.updated) else "failed")
        run.error_message = "\n".join(errors)[:2000] if errors else None

        try:
            self.db.commit()
        except Exception as exc:  # pragma: no cover - db hiccup
            logger.error(f"[{provider.name}] could not persist run row: {exc}")
            self.db.rollback()

        status = run.status if run.status != "running" else "success"
        return ProviderReport(
            provider=provider.name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            records_fetched=records_fetched,
            records_inserted=run.records_inserted,
            records_updated=run.records_updated,
            records_skipped=run.records_skipped,
            duplicates_removed=run.duplicates_removed,
            expired_marked=run.expired_marked,
            duration_ms=duration_ms,
            error_message=run.error_message,
        )

    def _touch_control(self, *, mode: str) -> None:
        control = self.db.query(SyncControl).first()
        if control is None:
            control = SyncControl(id=1, is_paused=False)
            self.db.add(control)
        if mode == "full":
            control.last_full_sync_at = datetime.utcnow()
        # Schedule the next run for "tomorrow at 03:00 local time" — the
        # scheduler will overwrite this if it has its own schedule.
        control.next_scheduled_sync_at = datetime.utcnow() + timedelta(days=1)
        control.updated_at = datetime.utcnow()
        try:
            self.db.commit()
        except Exception:  # pragma: no cover - best effort
            self.db.rollback()

    @staticmethod
    def _report_to_dict(report: ProviderReport) -> Dict:
        return {
            "provider": report.provider,
            "status": report.status,
            "started_at": report.started_at.isoformat(),
            "finished_at": report.finished_at.isoformat() if report.finished_at else None,
            "duration_ms": round(report.duration_ms, 2) if report.duration_ms else None,
            "records_fetched": report.records_fetched,
            "records_inserted": report.records_inserted,
            "records_updated": report.records_updated,
            "records_skipped": report.records_skipped,
            "duplicates_removed": report.duplicates_removed,
            "expired_marked": report.expired_marked,
            "error_message": report.error_message,
        }


__all__ = ["SyncEngine", "ProviderReport"]
