"""Google Patents provider.

**Disabled by default** — the Lens Patent API is the sole source of
truth for the patent analytics module.  This provider remains in the
registry so legacy code that references the class still works, but it
is never selected by the sync engine.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.logging import logger
from app.patents.core.base import (
    BasePatentProvider,
    NormalizedPatent,
    PatentProviderBatch,
    ProviderError,
)
from app.patents.core.config import patent_intel_settings
from app.patents.core.http_client import PatentProviderHTTPClient
from app.patents.core.registry import register_patent_provider


@register_patent_provider
class GooglePatentsProvider(BasePatentProvider):
    """Adapter for Google Patents public patent search."""

    name = "google_patents"

    def __init__(self) -> None:
        super().__init__(name=self.name)
        s = patent_intel_settings
        self._client: Optional[PatentProviderHTTPClient] = None
        self._base_url = s.GOOGLE_PATENTS_BASE_URL
        self._page_size = s.SYNC_PAGE_SIZE
        # Provider is disabled by default; no in-memory state needed.
        self._exhausted = True

    async def initialize(self) -> None:
        # Disabled by default — see module docstring.  We still allow
        # construction so the registry import succeeds; the health
        # snapshot will report ``disabled``.
        return None

    async def aclose(self) -> None:
        return None

    async def fetch_batch(
        self,
        *,
        cursor: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> PatentProviderBatch:
        # Disabled — no records returned.
        self._record_success(0.0)
        return PatentProviderBatch(records=[], next_cursor=None, total_estimated=0)

    def normalize(self, raw: Dict[str, Any]) -> Optional[NormalizedPatent]:
        if not isinstance(raw, dict):
            return None
        patent_number = (raw.get("patent_number") or raw.get("publication_number") or "").strip()
        if not patent_number:
            return None
        title = (raw.get("title") or "").strip()
        if not title:
            return None
        return NormalizedPatent(
            source=self.name,
            source_id=str(raw.get("source_id") or raw.get("publication_number") or patent_number),
            patent_number=patent_number,
            title=title,
            abstract=raw.get("abstract"),
            inventors=raw.get("inventors"),
            assignee=raw.get("assignee"),
            country=raw.get("country"),
            classification=raw.get("classification"),
            classification_label=raw.get("classification_label"),
            technology_area=raw.get("technology_area"),
            keywords=raw.get("keywords"),
            filing_date=raw.get("filing_date") if isinstance(raw.get("filing_date"), datetime) else None,
            publication_date=raw.get("publication_date") if isinstance(raw.get("publication_date"), datetime) else None,
            publication_year=raw.get("publication_year"),
            citations=int(raw.get("citations") or 0),
            patent_family=raw.get("patent_family"),
            legal_status=raw.get("legal_status"),
            url=raw.get("url"),
            extra_metadata=raw.get("extra_metadata") or {},
        )
