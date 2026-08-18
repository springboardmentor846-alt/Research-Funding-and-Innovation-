"""Patent Intelligence configuration.

Loads provider configuration from environment variables with safe
defaults so the service is opt-in per provider.  The structure mirrors
``funding_intel.core.config`` so an admin can read the two side by
side.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict

from pydantic_settings import BaseSettings


class PatentIntelSettings(BaseSettings):
    """Top-level settings for the Patent Intelligence Service."""

    # ------------------------------------------------------------------
    # Master switch
    # ------------------------------------------------------------------
    ENABLED: bool = True

    # Run an initial sync when the app starts (off by default in dev).
    RUN_INITIAL_SYNC_ON_STARTUP: bool = False

    # ------------------------------------------------------------------
    # Provider toggles
    # ------------------------------------------------------------------
    # The Lens Patent API is the **sole** source of truth for the
    # patent analytics module.  Google Patents and USPTO are kept in
    # the registry for backward compatibility but are off by default;
    # they were never stable enough to power the dashboard on their
    # own.
    GOOGLE_PATENTS_ENABLED: bool = False
    USPTO_ENABLED: bool = False
    THE_LENS_ENABLED: bool = True

    # ------------------------------------------------------------------
    # Provider endpoints
    # ------------------------------------------------------------------
    # Google Patents doesn't expose a stable public API.  We use the
    # PatentsView-compatible search interface that Google hosts for
    # its public dataset and fall back to a small built-in demo set
    # when the network is unreachable.
    GOOGLE_PATENTS_BASE_URL: str = "https://patents.google.com/xhr"
    USPTO_BASE_URL: str = "https://api.patentsview.org/patents/query"
    THE_LENS_BASE_URL: str = "https://api.lens.org"

    # ------------------------------------------------------------------
    # Provider credentials
    # ------------------------------------------------------------------
    LENS_API_TOKEN: str = ""

    # ------------------------------------------------------------------
    # HTTP
    # ------------------------------------------------------------------
    HTTP_TIMEOUT_SECONDS: float = 30.0
    HTTP_MAX_RETRIES: int = 3
    HTTP_RETRY_BACKOFF_SECONDS: float = 1.5
    HTTP_MAX_CONNECTIONS: int = 20
    HTTP_MAX_KEEPALIVE: int = 10
    HTTP_USER_AGENT: str = "ResearchFundingPlatform/1.0 (+patent-intel)"

    # ------------------------------------------------------------------
    # Sync
    # ------------------------------------------------------------------
    SYNC_PAGE_SIZE: int = 50
    SYNC_MAX_PAGES_PER_RUN: int = 5

    # ------------------------------------------------------------------
    # Scheduler
    # ------------------------------------------------------------------
    DAILY_SYNC_CRON: str = "0 5 * * *"
    WEEKLY_CLEANUP_CRON: str = "0 6 * * 0"

    # ------------------------------------------------------------------
    # Cache
    # ------------------------------------------------------------------
    PROVIDER_HEALTH_CACHE_SECONDS: int = 60
    SYNC_STATUS_CACHE_SECONDS: int = 5

    class Config:
        env_file = str(Path(__file__).resolve().parents[2] / ".env")
        case_sensitive = True
        extra = "ignore"


@lru_cache(maxsize=1)
def get_settings() -> PatentIntelSettings:
    return PatentIntelSettings()


patent_intel_settings = get_settings()


def provider_flags() -> Dict[str, bool]:
    s = get_settings()
    return {
        "google_patents": s.GOOGLE_PATENTS_ENABLED,
        "uspto": s.USPTO_ENABLED,
        "the_lens": s.THE_LENS_ENABLED,
    }
