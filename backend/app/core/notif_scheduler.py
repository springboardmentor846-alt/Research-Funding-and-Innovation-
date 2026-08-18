"""Lightweight background scheduler for notification housekeeping.

The platform already runs two APScheduler instances (funding intel
and patent intel).  This module is a tiny companion that:

* fires a funding-deadline scan once a day,
* is started from the FastAPI ``lifespan`` hook,
* exposes ``start_notif_scheduler`` / ``stop_notif_scheduler`` so
  ``app.main`` can wire it without modification beyond the two new
  calls.

The deadline scan is implemented in
``app.services.notification_service.run_funding_deadline_scan`` and
is fully idempotent via the dedup_key.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.logging import logger
from app.services.notification_service import run_funding_deadline_scan


_scheduler: Optional[AsyncIOScheduler] = None


async def _deadline_scan_job() -> None:
    """Run the funding-deadline scan (default window = 7 days)."""
    try:
        n = await asyncio.to_thread(run_funding_deadline_scan, 7)
        logger.info(f"[notif_scheduler] deadline scan considered {n} funding rows")
    except Exception as exc:  # pragma: no cover - scheduler guard
        logger.warning(f"[notif_scheduler] deadline scan failed: {exc}")


def start_notif_scheduler() -> AsyncIOScheduler:
    """Start the notification scheduler (idempotent)."""
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return _scheduler
    _scheduler = AsyncIOScheduler(timezone="UTC")
    # Daily at 09:00 UTC — a polite, off-peak hour that lines up with
    # the funding intel daily sync.
    _scheduler.add_job(
        _deadline_scan_job,
        CronTrigger.from_crontab("0 9 * * *"),
        id="notif_deadline_scan",
        name="Notifications: Daily Funding Deadline Scan",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    _scheduler.start()
    logger.info("[notif_scheduler] started")
    return _scheduler


def stop_notif_scheduler() -> None:
    """Stop the notification scheduler (safe to call multiple times)."""
    global _scheduler
    if _scheduler is None:
        return
    try:
        _scheduler.shutdown(wait=False)
    except Exception:  # pragma: no cover
        pass
    _scheduler = None
