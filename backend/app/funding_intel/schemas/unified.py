"""Unified funding schema for the Funding Intelligence Service.

These models are the public surface used by the admin API and by the
sync engine. The internal :class:`NormalizedFunding` dataclass is the
contract providers use; these Pydantic models are what the rest of the
HTTP world sees.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Unified funding schema (create/update/read)
# ---------------------------------------------------------------------------
class UnifiedFundingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1, max_length=64)
    source_id: str = Field(..., min_length=1, max_length=255)

    keywords: Optional[str] = None
    research_domain: Optional[str] = None
    organization: Optional[str] = None
    country: Optional[str] = None
    funding_type: Optional[str] = None
    category: Optional[str] = None
    research_area: Optional[str] = None
    eligibility: Optional[str] = None
    agency: Optional[str] = None

    funding_amount: Optional[float] = None
    currency: Optional[str] = None
    minimum_amount: Optional[float] = None
    maximum_amount: Optional[float] = None

    deadline: Optional[datetime] = None
    posted_date: Optional[datetime] = None
    status: Optional[str] = None

    source_url: Optional[str] = None


class UnifiedFundingCreate(UnifiedFundingBase):
    is_active: bool = True
    extra_metadata: Optional[Dict[str, Any]] = None


class UnifiedFundingUpdate(BaseModel):
    """Partial update payload; every field optional."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, min_length=1)
    keywords: Optional[str] = None
    research_domain: Optional[str] = None
    organization: Optional[str] = None
    country: Optional[str] = None
    funding_type: Optional[str] = None
    category: Optional[str] = None
    research_area: Optional[str] = None
    eligibility: Optional[str] = None
    agency: Optional[str] = None
    funding_amount: Optional[float] = None
    currency: Optional[str] = None
    minimum_amount: Optional[float] = None
    maximum_amount: Optional[float] = None
    deadline: Optional[datetime] = None
    posted_date: Optional[datetime] = None
    status: Optional[str] = None
    source_url: Optional[str] = None
    is_active: Optional[bool] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class UnifiedFundingResponse(UnifiedFundingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    last_synced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    extra_metadata: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Sync control / observability
# ---------------------------------------------------------------------------
class SyncRunRequest(BaseModel):
    """Request to trigger a sync."""

    provider: Optional[str] = Field(
        None,
        description="Restrict the run to a single provider. Default: all enabled providers.",
    )
    mode: str = Field(
        "incremental",
        pattern="^(incremental|full)$",
        description="Incremental = use cursor; full = ignore cursor and re-fetch.",
    )
    force: bool = Field(
        False,
        description="If true, run even when the global pause flag is set.",
    )


class SyncRunResponse(BaseModel):
    run_id: int
    provider: Optional[str] = None
    mode: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: str
    records_fetched: int
    records_inserted: int
    records_updated: int
    records_skipped: int
    duplicates_removed: int
    expired_marked: int
    errors: List[str] = []
    message: Optional[str] = None


class ProviderHealthResponse(BaseModel):
    name: str
    enabled: bool
    status: str
    last_checked: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    last_error: Optional[str] = None
    last_response_ms: Optional[float] = None
    consecutive_failures: int = 0


class SyncLogResponse(BaseModel):
    items: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int


class FailedRecordResponse(BaseModel):
    items: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int


class FundingIntelDashboardResponse(BaseModel):
    """Top-level admin dashboard payload."""

    apis_connected: int
    apis_enabled: int
    apis_healthy: int
    apis_degraded: int
    apis_error: int

    sync_status: str            # running | idle | paused | error
    last_sync_at: Optional[datetime] = None
    next_sync_at: Optional[datetime] = None

    funding_total: int
    funding_active: int
    funding_imported_today: int
    funding_updated_today: int
    duplicates_removed_today: int
    expired_today: int

    avg_response_time_ms: Optional[float] = None
    error_rate_pct: Optional[float] = None

    providers: List[ProviderHealthResponse] = []
    recent_runs: List[SyncRunResponse] = []
