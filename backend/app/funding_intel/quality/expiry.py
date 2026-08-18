"""Expiry / status helpers for funding opportunities.

A funding opportunity is *expired* when its application deadline is in
the past (with an optional grace period). Expired records are kept in
the database but flagged ``is_active=False`` so they drop out of
recommendations and the public list.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from app.funding_intel.core.config import funding_intel_settings


def is_expired(deadline: Optional[datetime], *, grace_days: int = 0) -> bool:
    if not deadline:
        return False
    if grace_days < 0:
        grace_days = 0
    return deadline < (datetime.utcnow() - timedelta(days=grace_days))


def compute_status(deadline: Optional[datetime], raw_status: Optional[str] = None) -> str:
    """Return one of ``open`` / ``closed`` / ``forecast``.

    ``raw_status`` is the upstream-reported status, if any. We honour
    upstream intent (e.g. "forecasted") but defer to deadline-based
    classification when the upstream just says "open" without a
    deadline.
    """
    raw = (raw_status or "").strip().lower()
    if raw in {"forecast", "forecasted", "pre-solicitation"}:
        return "forecast"
    if raw in {"closed", "expired", "archived"}:
        return "closed"
    if is_expired(deadline):
        return "closed"
    return "open"


def expiry_cursor(now: Optional[datetime] = None) -> datetime:
    """Return the ``updated_at`` cut-off below which rows should be re-validated.

    Implemented as ``now - EXPIRY_AFTER_DAYS``. With
    ``EXPIRY_AFTER_DAYS=0`` (default) the cut-off is "now", meaning any
    record touched today is fresh.
    """
    now = now or datetime.utcnow()
    days = max(0, funding_intel_settings.EXPIRY_AFTER_DAYS)
    return now - timedelta(days=days)
