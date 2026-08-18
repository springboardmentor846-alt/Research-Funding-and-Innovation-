"""Provider contracts for the Patent Intelligence Service.

A *provider* is a fully isolated adapter that knows how to talk to a
single external patent data source.  The rest of the system never
imports provider code directly; it goes through the registry and the
``BasePatentProvider`` interface below.

Each provider:

* Owns its own HTTP client, timeouts, retries, and error handling.
* Knows how to query its source for a bounded slice of patents
  (``fetch_batch``).
* Knows how to translate raw source payloads into ``NormalizedPatent``
  instances.
* Emits ``PatentProviderHealth`` snapshots on demand for the admin
  dashboard.
* Never raises to the caller; failures are reported via
  ``ProviderError`` and logged.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional

from app.patents.quality.normalization import normalize_patent_record


class ProviderError(RuntimeError):
    """Raised by providers when an external request fails irrecoverably.

    Providers should attempt their own retries/backoff before raising.
    The caller is expected to log the error and continue with the
    remaining providers.
    """


@dataclass
class PatentProviderHealth:
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
class NormalizedPatent:
    """Provider-agnostic, fully-validated patent record.

    Created by ``BasePatentProvider.normalize`` from a raw source
    payload.  The ingestion service is responsible for mapping these
    to the existing ``Patent`` SQLAlchemy row using
    ``app.patents.quality.normalization.normalize_patent_record``.
    """

    # Identity (required)
    source: str                            # google_patents | uspto | the_lens
    source_id: str                         # provider-specific unique id

    # Core content (required)
    patent_number: str
    title: str
    abstract: Optional[str] = None

    # Origin
    inventors: Optional[str] = None        # comma-separated
    assignee: Optional[str] = None
    country: Optional[str] = None

    # Classification
    classification: Optional[str] = None
    classification_label: Optional[str] = None
    technology_area: Optional[str] = None
    keywords: Optional[str] = None         # comma-separated

    # Dates
    filing_date: Optional[datetime] = None
    publication_date: Optional[datetime] = None
    publication_year: Optional[int] = None

    # Bibliometrics
    citations: int = 0
    patent_family: Optional[str] = None
    legal_status: Optional[str] = None

    # Provenance
    url: Optional[str] = None
    extra_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """JSON-safe representation used for logs and audit."""
        return {
            "source": self.source,
            "source_id": self.source_id,
            "patent_number": self.patent_number,
            "title": self.title,
            "abstract": self.abstract,
            "inventors": self.inventors,
            "assignee": self.assignee,
            "country": self.country,
            "classification": self.classification,
            "classification_label": self.classification_label,
            "technology_area": self.technology_area,
            "keywords": self.keywords,
            "filing_date": self.filing_date.isoformat() if self.filing_date else None,
            "publication_date": self.publication_date.isoformat() if self.publication_date else None,
            "publication_year": self.publication_year,
            "citations": self.citations,
            "patent_family": self.patent_family,
            "legal_status": self.legal_status,
            "url": self.url,
            "extra_metadata": self.extra_metadata,
        }

    def to_patent_create_dict(self) -> Dict[str, Any]:
        """Map to the dict shape ``PatentCreate`` expects.

        Delegates to the canonical normalizer so the provider layer
        can stay thin and the normalization rules live in one place.
        """
        return normalize_patent_record(self.to_dict(), source=self.source)


class BasePatentProvider(abc.ABC):
    """Abstract base class every patent provider must implement."""

    #: Lowercase, snake_case identifier; e.g. "google_patents".
    name: str = ""

    def __init__(self, *, name: str) -> None:
        self.name = name
        self._health = PatentProviderHealth(name=name, enabled=True)

    # -- Lifecycle ---------------------------------------------------------
    @abc.abstractmethod
    async def initialize(self) -> None:
        """Set up HTTP clients, validate configuration, etc."""

    async def aclose(self) -> None:
        """Release resources. Default: no-op."""

    # -- Health ------------------------------------------------------------
    def health(self) -> PatentProviderHealth:
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
        page_size: int = 50,
    ) -> "PatentProviderBatch":
        """Fetch a single bounded batch from the upstream.

        ``cursor`` is provider-specific opaque state used for resumable
        incremental sync.  ``None`` means "start from the beginning".
        Returns a :class:`PatentProviderBatch` containing the raw
        payloads for this page plus the cursor to use for the next
        call (or ``None`` when the upstream is exhausted).
        """

    @abc.abstractmethod
    def normalize(self, raw: Dict[str, Any]) -> Optional[NormalizedPatent]:
        """Translate a single raw upstream record into a ``NormalizedPatent``.

        Returning ``None`` signals that the record is unsalvageable and
        should be skipped.  Providers should never raise from this
        method.
        """


@dataclass
class PatentProviderBatch:
    """A single page of raw upstream records plus a next-page cursor."""

    records: List[Dict[str, Any]] = field(default_factory=list)
    next_cursor: Optional[str] = None
    total_estimated: Optional[int] = None


@dataclass
class PatentProviderRunResult:
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
