"""Provider contracts and shared primitives.

A *provider* is a fully-isolated adapter that knows how to talk to a
single external funding data source. The rest of the system never
imports provider code directly; it goes through the registry and
through the ``BaseProvider`` interface below.

Each provider:

* Owns its own HTTP client, timeouts, retries, and error handling.
* Knows how to query its source for a bounded slice of opportunities
  (``fetch_batch``).
* Knows how to translate raw source payloads into ``NormalizedFunding``
  instances.
* Emits ``ProviderHealth`` snapshots on demand for the admin dashboard.
* Never raises to the caller; failures are reported via
  ``ProviderError`` and logged.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional


class ProviderError(RuntimeError):
    """Raised by providers when an external request fails irrecoverably.

    Providers should attempt their own retries/backoff before raising.
    The caller is expected to log the error and continue with the
    remaining providers.
    """


@dataclass
class ProviderHealth:
    """Snapshot of a single provider's health for the admin dashboard."""

    name: str
    enabled: bool
    last_checked: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    last_error: Optional[str] = None
    last_response_ms: Optional[float] = None
    consecutive_failures: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "enabled": self.enabled,
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None,
            "last_error": self.last_error,
            "last_response_ms": self.last_response_ms,
            "consecutive_failures": self.consecutive_failures,
            "status": self._status(),
        }

    def _status(self) -> str:
        if not self.enabled:
            return "disabled"
        if self.consecutive_failures == 0 and self.last_success:
            return "healthy"
        if self.consecutive_failures >= 3:
            return "degraded"
        if self.last_failure and (not self.last_success or self.last_failure > self.last_success):
            return "error"
        return "unknown"


@dataclass
class NormalizedFunding:
    """Provider-agnostic, fully-validated funding opportunity.

    Created by ``BaseProvider.normalize`` from a raw source payload. The
    ingestion service is responsible for mapping these to the existing
    ``Funding`` SQLAlchemy row.
    """

    # Identity (required)
    source: str                            # e.g. "nih", "grants_gov", "nsf", "cordis"
    source_id: str                         # provider-specific unique id

    # Core content (required)
    title: str
    description: str

    # Origin (optional but recommended)
    agency: Optional[str] = None
    organization: Optional[str] = None
    country: Optional[str] = None

    # Classification (optional)
    category: Optional[str] = None
    keywords: Optional[str] = None         # comma-separated
    research_area: Optional[str] = None
    funding_type: Optional[str] = None
    eligibility: Optional[str] = None

    # Money (optional)
    funding_amount: Optional[float] = None
    currency: Optional[str] = None
    minimum_amount: Optional[float] = None
    maximum_amount: Optional[float] = None

    # Dates (optional)
    deadline: Optional[datetime] = None
    posted_date: Optional[datetime] = None

    # Status (optional)
    status: Optional[str] = None           # open | closed | forecast

    # Provenance
    source_url: Optional[str] = None
    last_updated: Optional[datetime] = None
    extra_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """JSON-safe representation (used for logs/audit)."""
        return {
            "source": self.source,
            "source_id": self.source_id,
            "title": self.title,
            "description": self.description,
            "agency": self.agency,
            "organization": self.organization,
            "country": self.country,
            "category": self.category,
            "keywords": self.keywords,
            "research_area": self.research_area,
            "funding_type": self.funding_type,
            "eligibility": self.eligibility,
            "funding_amount": self.funding_amount,
            "currency": self.currency,
            "minimum_amount": self.minimum_amount,
            "maximum_amount": self.maximum_amount,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "posted_date": self.posted_date.isoformat() if self.posted_date else None,
            "status": self.status,
            "source_url": self.source_url,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "extra_metadata": self.extra_metadata,
        }


class BaseProvider(abc.ABC):
    """Abstract base class every provider must implement."""

    #: Lowercase, hyphen-free identifier; e.g. "nih", "grants_gov".
    name: str = ""

    def __init__(self, *, name: str) -> None:
        self.name = name
        self._health = ProviderHealth(name=name, enabled=True)

    # -- Lifecycle ---------------------------------------------------------
    @abc.abstractmethod
    async def initialize(self) -> None:
        """Set up HTTP clients, validate configuration, etc."""

    async def aclose(self) -> None:
        """Release resources. Default: no-op."""

    # -- Health ------------------------------------------------------------
    def health(self) -> ProviderHealth:
        return self._health

    def _record_success(self, elapsed_ms: float) -> None:
        from datetime import datetime as _dt
        self._health.last_checked = _dt.utcnow()
        self._health.last_success = self._health.last_checked
        self._health.last_response_ms = elapsed_ms
        self._health.consecutive_failures = 0
        self._health.last_error = None

    def _record_failure(self, message: str) -> None:
        from datetime import datetime as _dt
        self._health.last_checked = _dt.utcnow()
        self._health.last_failure = self._health.last_checked
        self._health.last_error = message[:500]
        self._health.consecutive_failures += 1

    # -- Sync entry points -------------------------------------------------
    @abc.abstractmethod
    async def fetch_batch(
        self,
        *,
        cursor: Optional[str] = None,
        page_size: int = 100,
    ) -> "ProviderBatch":
        """Fetch a single bounded batch from the upstream.

        ``cursor`` is provider-specific opaque state used for resumable
        incremental sync. ``None`` means "start from the beginning".
        Returns a :class:`ProviderBatch` containing the raw payloads
        for this page plus the cursor to use for the next call (or
        ``None`` when the upstream is exhausted).
        """

    @abc.abstractmethod
    def normalize(self, raw: Dict[str, Any]) -> Optional[NormalizedFunding]:
        """Translate a single raw upstream record into a ``NormalizedFunding``.

        Returning ``None`` signals that the record is unsalvageable and
        should be skipped. Providers should never raise from this method.
        """


@dataclass
class ProviderBatch:
    """A single page of raw upstream records plus a next-page cursor."""

    records: List[Dict[str, Any]] = field(default_factory=list)
    next_cursor: Optional[str] = None
    total_estimated: Optional[int] = None


@dataclass
class ProviderRunResult:
    """Outcome of a full provider run (multiple batches)."""

    provider: str
    records_fetched: int = 0
    records_normalized: int = 0
    records_skipped: int = 0
    errors: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    cursor_at_start: Optional[str] = None
    cursor_at_end: Optional[str] = None
    success: bool = True
