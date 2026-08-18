"""Funding Intelligence configuration.

Loads provider configuration from environment variables with safe
defaults so the service is opt-in per provider.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Dict

from pydantic_settings import BaseSettings


class FundingIntelSettings(BaseSettings):
    """Top-level settings for the Funding Intelligence Service."""

    # ------------------------------------------------------------------
    # Master switch
    # ------------------------------------------------------------------
    ENABLED: bool = True

    # IMPORTANT:
    # Disable automatic sync during development.
    # You can trigger sync manually from the API.
    RUN_INITIAL_SYNC_ON_STARTUP: bool = False

    # ------------------------------------------------------------------
    # Provider toggles
    # ------------------------------------------------------------------
    NIH_ENABLED: bool = True
    GRANTSGOV_ENABLED: bool = True
    NSF_ENABLED: bool = True
    OPENALEX_ENABLED: bool =True

    # Not using CORDIS
    CORDIS_ENABLED: bool = False

    # ------------------------------------------------------------------
    # Provider endpoints
    # ------------------------------------------------------------------
    NIH_BASE_URL: str = "https://api.reporter.nih.gov/v2"
    GRANTSGOV_BASE_URL: str = "https://api.grants.gov/v1/api"
    NSF_BASE_URL: str = "https://api.nsf.gov/services/v1"
    OPENALEX_BASE_URL: str = "https://api.openalex.org"
    CORDIS_BASE_URL: str = "https://cordis.europa.eu/api"

    # ------------------------------------------------------------------
    # Provider credentials
    # ------------------------------------------------------------------
    OPENALEX_API_KEY: str = "CwmB72B1SemWbHUco8bAs0"
    OPENALEX_MAILTO: str = "funding-intel@research-platform.local"

    # ------------------------------------------------------------------
    # HTTP
    # ------------------------------------------------------------------
    HTTP_TIMEOUT_SECONDS: float = 30.0
    HTTP_MAX_RETRIES: int = 3
    HTTP_RETRY_BACKOFF_SECONDS: float = 1.5
    HTTP_MAX_CONNECTIONS: int = 20
    HTTP_MAX_KEEPALIVE: int = 10
    HTTP_USER_AGENT: str = "ResearchFundingPlatform/1.0 (+funding-intel)"

    # ------------------------------------------------------------------
    # Sync
    # ------------------------------------------------------------------
    SYNC_BATCH_SIZE: int = 20
    SYNC_PAGE_SIZE: int = 20

    # Only fetch 2 pages from each provider while testing
    SYNC_MAX_PAGES_PER_RUN: int = 2

    EXPIRY_AFTER_DAYS: int = 0
    RECENT_SYNCS_WINDOW_DAYS: int = 30

    # ------------------------------------------------------------------
    # Scheduler
    # ------------------------------------------------------------------
    DAILY_SYNC_CRON: str = "0 3 * * *"
    WEEKLY_CLEANUP_CRON: str = "0 4 * * 0"

    # ------------------------------------------------------------------
    # Cache
    # ------------------------------------------------------------------
    PROVIDER_HEALTH_CACHE_SECONDS: int = 60
    SYNC_STATUS_CACHE_SECONDS: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache(maxsize=1)
def get_settings() -> FundingIntelSettings:
    return FundingIntelSettings()


funding_intel_settings = get_settings()


def provider_flags() -> Dict[str, bool]:
    s = get_settings()

    return {
        "nih": s.NIH_ENABLED,
        "grants_gov": s.GRANTSGOV_ENABLED,
        "nsf": s.NSF_ENABLED,
        "openalex": s.OPENALEX_ENABLED,
        "cordis": s.CORDIS_ENABLED,
    }