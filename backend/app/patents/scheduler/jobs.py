"""Scheduled background jobs for the Patent Intelligence Service.

We use ``APScheduler`` (``AsyncIOScheduler``) so the same event loop
that serves FastAPI requests also drives the periodic sync.  The
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
from app.patents.core.config import patent_intel_settings
from app.patents.services.sync import PatentSyncEngine


_scheduler: Optional[AsyncIOScheduler] = None


async def _run_initial_sync_once() -> None:
    """Trigger a one-off startup sync and log any failure."""
    try:
        logger.info("[patent-scheduler] starting initial patent sync")
        await daily_patent_sync_job()
    except Exception as exc:  # pragma: no cover - startup guard
        logger.exception(f"[patent-scheduler] initial patent sync failed: {exc}")


def _trigger_initial_sync() -> None:
    """Schedule a one-off initial sync when the app starts."""
    if not patent_intel_settings.RUN_INITIAL_SYNC_ON_STARTUP:
        return
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        logger.warning("[patent-scheduler] no running event loop available for initial sync")
        return

    loop.create_task(_run_initial_sync_once())
    logger.info("[patent-scheduler] initial patent sync scheduled")


async def daily_patent_sync_job() -> dict:
    """Incremental patent sync of every enabled provider."""
    engine = PatentSyncEngine()
    try:
        result = await engine.run(mode="incremental")
        logger.info(f"[patent-scheduler] daily sync finished: {result.get('status')}")
        return result
    finally:
        if engine._owns_session:
            engine.db.close()


async def weekly_patent_cleanup_job() -> dict:
    """Weekly: full sync."""
    engine = PatentSyncEngine()
    try:
        result = await engine.run(mode="full")
        logger.info(f"[patent-scheduler] weekly cleanup finished: {result.get('status')}")
        return result
    finally:
        if engine._owns_session:
            engine.db.close()


async def patent_health_probe_job() -> None:
    """Touch each patent provider to record health."""
    from app.patents.core.registry import all_patent_providers

    providers = all_patent_providers()
    for prov in providers:
        try:
            await prov.initialize()
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
        logger.error(f"[patent-scheduler] job failed: {event.exception}")
    else:
        logger.debug(f"[patent-scheduler] job {event.job_id} completed")


def build_patent_scheduler() -> AsyncIOScheduler:
    """Construct the AsyncIOScheduler with the configured crons."""
    s = patent_intel_settings
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_listener(
        _scheduler_event_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
    )
    scheduler.add_job(
        daily_patent_sync_job,
        CronTrigger.from_crontab(s.DAILY_SYNC_CRON),
        id="patent_daily_sync",
        name="Patent Intel: Daily Incremental Sync",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        weekly_patent_cleanup_job,
        CronTrigger.from_crontab(s.WEEKLY_CLEANUP_CRON),
        id="patent_weekly_cleanup",
        name="Patent Intel: Weekly Full Sync",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        patent_health_probe_job,
        CronTrigger.from_crontab("*/30 * * * *"),
        id="patent_health_probe",
        name="Patent Intel: Provider Health Probe",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    return scheduler


def start_patent_scheduler() -> AsyncIOScheduler:
    """Start the global scheduler (idempotent)."""
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return _scheduler
    _scheduler = build_patent_scheduler()
    _scheduler.start()
    _trigger_initial_sync()
    logger.info("[patent-scheduler] patent intel background jobs started")
    return _scheduler


def stop_patent_scheduler() -> None:
    """Stop the global scheduler (safe to call multiple times)."""
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        try:
            _scheduler.shutdown(wait=False)
        except Exception as exc:  # pragma: no cover
            logger.warning(f"[patent-scheduler] shutdown error: {exc}")
    _scheduler = None


def patent_scheduler_running() -> bool:
    return _scheduler is not None and _scheduler.running
