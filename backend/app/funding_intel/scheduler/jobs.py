"""Scheduled background jobs for the Funding Intelligence Service.

We use ``APScheduler`` (``AsyncIOScheduler``) so the same event loop
that serves FastAPI requests also drives the periodic sync. The
scheduler is started once during application lifespan and shut down
cleanly on application stop.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from app.core.logging import logger
from app.funding_intel.core.config import funding_intel_settings
from app.funding_intel.models import SyncControl
from app.funding_intel.services.sync import SyncEngine
from app.db import SessionLocal


_scheduler: Optional[AsyncIOScheduler] = None


async def _run_initial_sync_once() -> None:
    """Trigger a one-off startup sync and log any failure."""
    try:
        logger.info("[scheduler] starting initial funding sync")
        await daily_sync_job()
    except Exception as exc:  # pragma: no cover - startup guard
        logger.exception(f"[scheduler] initial funding sync failed: {exc}")


def _trigger_initial_sync() -> None:
    """Schedule a one-off initial sync when the app starts."""
    if not funding_intel_settings.RUN_INITIAL_SYNC_ON_STARTUP:
        return
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        logger.warning("[scheduler] no running event loop available for initial sync")
        return

    loop.create_task(_run_initial_sync_once())
    logger.info("[scheduler] initial funding sync scheduled")


async def daily_sync_job() -> dict:
    """Incremental sync of every enabled provider."""
    engine = SyncEngine()
    try:
        result = await engine.run(mode="incremental")
        logger.info(f"[scheduler] daily sync finished: {result.get('status')}")
        return result
    finally:
        if engine._owns_session:
            engine.db.close()


async def weekly_cleanup_job() -> dict:
    """Weekly: full sync + mark expired rows.

    A full sync re-fetches all known opportunities without honouring
    per-provider cursors so that records which fell out of an
    incremental window still get a chance to update.
    """
    engine = SyncEngine()
    try:
        result = await engine.run(mode="full")
        # ``expire_stale`` already runs per provider; this is a belt-and-braces
        # second pass to catch anything ingested earlier today.
        from app.funding_intel.services.ingest import IngestService
        from app.funding_intel.models import SyncRun
        db = engine.db
        run = SyncRun(provider="cleanup", mode="full", status="running")
        db.add(run)
        db.commit()
        db.refresh(run)
        ingest = IngestService(db, run)
        n = ingest.expire_stale()
        run.finished_at = __import__("datetime").datetime.utcnow()
        run.expired_marked = n
        run.status = "success"
        db.commit()
        logger.info(f"[scheduler] weekly cleanup: marked {n} records expired")
        return result
    finally:
        if engine._owns_session:
            engine.db.close()


async def health_probe_job() -> None:
    """Hit each provider's health endpoint at most once per hour."""
    from app.funding_intel.core.registry import all_providers

    providers = all_providers()
    for prov in providers:
        try:
            await prov.initialize()
            # Use a tiny synthetic batch with a zero cursor; if the
            # provider raises we record a failure but never propagate.
            try:
                await prov.fetch_batch(cursor=None, page_size=1)
                prov._record_success(0.0)
            except Exception as exc:
                prov._record_failure(str(exc))
        except Exception as exc:
            prov._record_failure(str(exc))
        finally:
            try:
                await prov.aclose()
            except Exception:
                pass


def _scheduler_event_listener(event):
    """Surface scheduler events into the application log."""
    if event.exception:
        logger.error(f"[scheduler] job failed: {event.exception}")
    else:
        logger.debug(f"[scheduler] job {event.job_id} completed")


def build_scheduler() -> AsyncIOScheduler:
    """Construct the AsyncIOScheduler with the configured crons."""
    s = funding_intel_settings
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_listener(_scheduler_event_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    scheduler.add_job(
        daily_sync_job,
        CronTrigger.from_crontab(s.DAILY_SYNC_CRON),
        id="daily_sync",
        name="Funding Intel: Daily Incremental Sync",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        weekly_cleanup_job,
        CronTrigger.from_crontab(s.WEEKLY_CLEANUP_CRON),
        id="weekly_cleanup",
        name="Funding Intel: Weekly Full Sync & Cleanup",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        health_probe_job,
        CronTrigger.from_crontab("*/15 * * * *"),
        id="health_probe",
        name="Funding Intel: Provider Health Probe",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    return scheduler


def start_scheduler() -> AsyncIOScheduler:
    """Start the global scheduler (idempotent)."""
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return _scheduler
    _scheduler = build_scheduler()
    _scheduler.start()
    _trigger_initial_sync()
    logger.info("[scheduler] funding intel background jobs started")
    return _scheduler


def stop_scheduler() -> None:
    """Stop the global scheduler (safe to call multiple times)."""
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        try:
            _scheduler.shutdown(wait=False)
        except Exception as exc:  # pragma: no cover - shutdown best-effort
            logger.warning(f"[scheduler] shutdown error: {exc}")
    _scheduler = None


def scheduler_running() -> bool:
    return _scheduler is not None and _scheduler.running
