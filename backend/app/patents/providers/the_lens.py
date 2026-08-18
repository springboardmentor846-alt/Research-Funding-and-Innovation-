"""The Lens Patent API provider.

This is the **sole** patent data source for the platform.  The provider
wraps :class:`app.patents.providers.lens_client.LensPatentClient` and
translates raw upstream records into the canonical ``Patent`` row
shape used by the dashboard.

The provider exposes the full search surface area the dashboard needs:

* Keyword search
* Technology-domain search (CPC / IPC)
* Inventor search
* Assignee / applicant search
* Country / jurisdiction search
* Year-range / since-timestamp search
* Pagination (``fetch_batch`` honours the ``cursor`` parameter that
  the rest of the sync engine uses)
* Single-patent lookup by Lens id

Sync modes
----------

* ``incremental`` — only patents whose ``date_published`` is at or
  after ``last_synced_at`` (the most recent ``last_synced_at`` of any
  Patent row, or the value of ``SINCE_DATE_PUBLISHED`` if no row
  exists yet, falling back to ``2018-01-01``).
* ``full`` — every patent published from 2018-01-01 onwards (the
  Lens free trial only retains recent patents).

In both modes the **provider never falls back to mock / curated /
cached data**.  When the upstream is unreachable the error is
propagated so the SyncEngine can mark the run as failed and surface
the error in the admin UI.

Deduplication
-------------

The provider emits a ``source_id`` equal to the upstream ``lens_id``
when available, falling back to the canonical ``publication_number``.
The database has a partial unique index on ``lens_id`` (migration
``0005_lens_patent_fields``) so duplicate inserts raise an
``IntegrityError``; the ingest service catches and treats that as an
update.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence

from app.core.logging import logger
from app.patents.core.base import (
    BasePatentProvider,
    NormalizedPatent,
    PatentProviderBatch,
    ProviderError,
)
from app.patents.core.config import patent_intel_settings
from app.patents.core.registry import register_patent_provider
from app.patents.providers.lens_client import (
    LensAuthError,
    LensClientConfig,
    LensError,
    LensNotFoundError,
    LensPatentClient,
    LensRateLimitError,
    LensSearchFilters,
    LensSearchResult,
)


# ----------------------------------------------------------------------------
# Default "since" timestamp for the first sync.  Used when the database has
# no patent rows yet so the first sync still has a sane lower bound.
# ----------------------------------------------------------------------------
DEFAULT_SINCE_DATE_PUBLISHED = "2018-01-01T00:00:00.000Z"


@register_patent_provider
class TheLensProvider(BasePatentProvider):
    """Adapter for The Lens public patent API.

    All HTTP traffic flows through :class:`LensPatentClient`, which
    handles authentication, retries, backoff, and rate-limiting.  This
    provider is a thin translation layer between the Lens envelope and
    the canonical ``Patent`` row shape.
    """

    name = "the_lens"

    def __init__(self) -> None:
        super().__init__(name=self.name)
        s = patent_intel_settings
        self._config = LensClientConfig(
            base_url=s.THE_LENS_BASE_URL,
            token=s.LENS_API_TOKEN,
            timeout_seconds=s.HTTP_TIMEOUT_SECONDS,
            max_retries=s.HTTP_MAX_RETRIES,
            backoff_seconds=s.HTTP_RETRY_BACKOFF_SECONDS,
            page_size=s.SYNC_PAGE_SIZE,
            user_agent=s.HTTP_USER_AGENT,
        )
        self._client: Optional[LensPatentClient] = None
        # Last successful search query and filters — used so the
        # SyncEngine can resume by re-issuing the same query from a
        # new offset.
        self._last_query: str = "*"
        self._last_filters: List[Mapping[str, Any]] = []

    # -- Lifecycle ---------------------------------------------------------

    async def initialize(self) -> None:
        if self._client is not None:
            return
        if not self._config.token:
            raise LensAuthError(
                "LENS_API_TOKEN is not configured; cannot initialise The Lens provider"
            )
        self._client = LensPatentClient(self._config)
        logger.info(
            f"[{self.name}] HTTP client initialised against {self._config.base_url}"
        )

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    # -- Sync entry point --------------------------------------------------

    async def fetch_batch(
        self,
        *,
        cursor: Optional[str] = None,
        page_size: Optional[int] = None,
        since: Optional[str] = None,
        mode: str = "incremental",
    ) -> PatentProviderBatch:
        """Fetch a single page of patents from The Lens.

        ``cursor`` is a JSON-encoded string of
        ``{"query": "...", "from": <int>, "filters": [...]}``.  When
        ``cursor`` is ``None`` we build a new search: incremental
        mode pins ``date_published >= since`` (or
        ``DEFAULT_SINCE_DATE_PUBLISHED`` if no ``since`` is given);
        full mode fetches everything from 2018-01-01 onwards.

        ``since`` is an ISO-8601 timestamp (the value the caller
        computed from the database's ``last_synced_at``).  It is
        ignored when ``mode != "incremental"``.
        """
        if self._client is None:
            await self.initialize()

        query, from_offset, filters = self._decode_cursor(
            cursor=cursor, mode=mode, since=since
        )
        self._last_query = query
        self._last_filters = list(filters)
        size = page_size or self._config.page_size

        started = time.perf_counter()
        try:
            result = await self._client.search(
                query=query,
                from_offset=from_offset,
                size=size,
                filters=filters or None,
            )
        except LensAuthError as exc:
            # Auth errors must not be retried — bubble up with a clear message.
            self._record_failure(str(exc))
            raise ProviderError(f"The Lens auth failed: {exc}") from exc
        except LensRateLimitError as exc:
            self._record_failure(f"rate limited: {exc}")
            raise ProviderError(f"The Lens rate limit hit: {exc}") from exc
        except LensError as exc:
            self._record_failure(str(exc))
            raise ProviderError(f"The Lens request failed: {exc}") from exc

        records = list(result.records)
        next_from = from_offset + len(records)
        next_cursor: Optional[str] = None
        if records and len(records) >= size:
            if result.total is None or next_from < result.total:
                next_cursor = self._encode_cursor(query, next_from, filters)

        elapsed_ms = (time.perf_counter() - started) * 1000.0
        self._record_success(elapsed_ms)
        logger.info(
            f"[{self.name}] mode={mode} page offset={from_offset} "
            f"size={len(records)} total={result.total} elapsed_ms={elapsed_ms:.1f}"
        )

        return PatentProviderBatch(
            records=records,
            next_cursor=next_cursor,
            total_estimated=result.total,
        )

    def normalize(self, raw: Dict[str, Any]) -> Optional[NormalizedPatent]:
        if not isinstance(raw, dict):
            return None
        try:
            return self._lens_to_normalized(raw)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning(f"[{self.name}] normalize failed: {exc}")
            return None

    # -- Convenience search methods ---------------------------------------

    async def search_by_keyword(
        self, text: str, *, size: int = 25, from_offset: int = 0
    ) -> LensSearchResult:
        await self._ensure_client()
        filters = list(LensSearchFilters.keyword(text))
        return await self._client.search(  # type: ignore[union-attr]
            query="*",
            from_offset=from_offset,
            size=size,
            filters=filters,
        )

    async def search_by_technology(
        self,
        *,
        cpc: Optional[str] = None,
        ipc: Optional[str] = None,
        size: int = 25,
        from_offset: int = 0,
    ) -> LensSearchResult:
        await self._ensure_client()
        filters = LensSearchFilters.combine(
            LensSearchFilters.technology_domain(cpc=cpc, ipc=ipc)
        )
        return await self._client.search(  # type: ignore[union-attr]
            query="*",
            from_offset=from_offset,
            size=size,
            filters=filters or None,
        )

    async def search_by_inventor(
        self, name: str, *, size: int = 25, from_offset: int = 0
    ) -> LensSearchResult:
        await self._ensure_client()
        filters = list(LensSearchFilters.inventor(name))
        return await self._client.search(  # type: ignore[union-attr]
            query="*",
            from_offset=from_offset,
            size=size,
            filters=filters or None,
        )

    async def search_by_assignee(
        self, name: str, *, size: int = 25, from_offset: int = 0
    ) -> LensSearchResult:
        await self._ensure_client()
        filters = list(LensSearchFilters.assignee(name))
        return await self._client.search(  # type: ignore[union-attr]
            query="*",
            from_offset=from_offset,
            size=size,
            filters=filters or None,
        )

    async def fetch_patent(self, lens_id: str) -> Dict[str, Any]:
        """Return the raw Lens envelope for a single patent by id."""
        await self._ensure_client()
        return await self._client.get_patent(lens_id)  # type: ignore[union-attr]

    # -- Internals ---------------------------------------------------------

    async def _ensure_client(self) -> None:
        if self._client is None:
            await self.initialize()

    def _encode_cursor(
        self,
        query: str,
        from_offset: int,
        filters: Sequence[Mapping[str, Any]],
    ) -> str:
        return json.dumps(
            {
                "query": query,
                "from": int(from_offset),
                "filters": [dict(f) for f in (filters or [])],
            },
            separators=(",", ":"),
        )

    def _decode_cursor(
        self,
        *,
        cursor: Optional[str],
        mode: str,
        since: Optional[str],
    ) -> tuple[str, int, List[Mapping[str, Any]]]:
        """Decode the pagination cursor or build the default filter set.

        When ``cursor`` is empty:
        * ``mode == "incremental"`` — pin ``date_published >= since``.
          ``since`` defaults to ``DEFAULT_SINCE_DATE_PUBLISHED``.
        * ``mode == "full"`` — fetch the same window (full mirrors
          incremental until we have a real "since" the operator
          defines).
        """
        if cursor:
            try:
                payload = json.loads(cursor)
                query = str(payload.get("query") or "*")
                from_offset = int(payload.get("from") or 0)
                raw_filters = payload.get("filters") or []
                filters: List[Mapping[str, Any]] = [
                    f for f in raw_filters if isinstance(f, dict)
                ]
                return query, from_offset, filters
            except (ValueError, TypeError):
                # Fall through to the default.
                pass

        # Default cursor — start at the beginning of the configured
        # window.
        since_iso = since or DEFAULT_SINCE_DATE_PUBLISHED
        filters: List[Mapping[str, Any]] = [
            {
                "range": {
                    "date_published": {"gte": since_iso},
                    # Cap far-future inserts to dodge a class of bugs.
                    "lte": "2100-01-01T00:00:00.000Z",
                }
            }
        ]
        return "*", 0, filters

    # -- Normalization -----------------------------------------------------

    @staticmethod
    def _coerce_int(value: Any) -> Optional[int]:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _coerce_str(value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            return value.strip() or None
        return str(value)

    def _lens_to_normalized(self, raw: Dict[str, Any]) -> Optional[NormalizedPatent]:
        """Turn a raw Lens record into a :class:`NormalizedPatent`.

        The ``create_dict`` is captured in ``extra_metadata`` so the
        ingest service can hydrate the Lens-specific columns on the
        ``Patent`` row (lens_id, ipc_classifications,
        cpc_classifications, etc.).  That roundtrip is the only way to
        thread those extra columns through the provider-agnostic
        ``NormalizedPatent`` contract without coupling it to a single
        upstream.
        """
        lens_id = self._coerce_str(raw.get("lens_id"))
        publication_number = self._coerce_str(raw.get("publication_number"))
        patent_number = publication_number or lens_id or ""
        if not patent_number:
            return None

        title = self._coerce_str(raw.get("title")) or ""
        abstract = (
            self._coerce_str(raw.get("abstract"))
            or self._coerce_str(raw.get("summary"))
        )
        inventors = self._format_inventors(raw.get("inventors"))
        assignees = self._format_applicants(raw.get("applicants") or raw.get("owners"))
        inventor_names = self._collect_names(raw.get("inventors"))
        applicant_names = self._collect_names(
            raw.get("applicants") or raw.get("owners")
        )
        cpc = self._collect_classifications(raw.get("cpc_classifications"))
        ipc = self._collect_classifications(raw.get("ipc_classifications"))
        classification = cpc[0] if cpc else (ipc[0] if ipc else None)
        country = self._coerce_str(raw.get("jurisdiction"))
        filing_date = self._coerce_datetime(raw.get("application_date"))
        publication_date = self._coerce_datetime(raw.get("publication_date"))
        publication_year = self._coerce_int(
            raw.get("publication_year")
        ) or (publication_date.year if publication_date else None)
        earliest_priority = self._coerce_datetime(
            raw.get("earliest_priority_date")
        )
        grant_date = self._coerce_datetime(raw.get("grant_date"))
        npl_cites = self._coerce_int(raw.get("npl_citations_count")) or 0
        patent_cites = self._coerce_int(
            raw.get("patent_citations_count")
            or raw.get("cited_by_patent_count")
        ) or 0
        total_cites = npl_cites + patent_cites
        family_size = self._coerce_int(
            raw.get("simple_family_size")
            or raw.get("extended_family_size")
        )
        legal_status = self._coerce_str(raw.get("legal_status"))
        if not legal_status and raw.get("is_grant") is True:
            legal_status = "granted"
        elif not legal_status and raw.get("is_grant") is False:
            legal_status = "pending"
        doc_type = self._coerce_str(raw.get("publication_type")) or self._coerce_str(
            raw.get("doc_type")
        )
        url = self._coerce_str(raw.get("lens_url")) or self._coerce_str(
            raw.get("url")
        )

        # ------------------------------------------------------------------
        # Standard fields (consumed by the SQLAlchemy ``Patent`` row).
        # ------------------------------------------------------------------
        standard = {
            "patent_number": patent_number,
            "title": title,
            "abstract": abstract,
            "inventors": inventors,
            "assignee": assignees,
            "technology_area": None,  # left for the normalizer
            "keywords": None,
            "country": country,
            "classification": classification,
            "classification_label": None,
            "filing_date": filing_date,
            "publication_date": publication_date,
            "publication_year": publication_year,
            "citations": total_cites,
            "patent_family": self._coerce_str(raw.get("family_id")) or None,
            "legal_status": legal_status,
            "source": self.name,
            # ``source_id`` is the dedup key.  Lens always has a unique
            # ``lens_id`` so we use that when present; the publication
            # number is a faithful fallback.
            "source_id": lens_id or publication_number or patent_number,
            "url": url,
        }

        # ------------------------------------------------------------------
        # Lens-specific fields.  Stored in ``extra_metadata`` under a
        # dedicated key so the ingest service can pick them up and
        # write them to the Patent row without polluting the
        # provider-agnostic schema.
        # ------------------------------------------------------------------
        lens_specific = {
            "lens_id": lens_id,
            "ipc_classifications": ipc or None,
            "cpc_classifications": cpc or None,
            "npl_citations_count": npl_cites,
            "patent_citations_count": patent_cites,
            "family_size": family_size,
            "earliest_priority_date": earliest_priority.isoformat()
            if earliest_priority
            else None,
            "grant_date": grant_date.isoformat() if grant_date else None,
            "applicant_names": applicant_names or None,
            "inventor_names": inventor_names or None,
            "jurisdiction": country,
            "doc_type": doc_type,
            "lens_url": url,
            "kind": self._coerce_str(raw.get("kind")),
            "simple_family_size": self._coerce_int(
                raw.get("simple_family_size")
            ),
            "extended_family_size": self._coerce_int(
                raw.get("extended_family_size")
            ),
            "us_classifications": self._collect_classifications(
                raw.get("us_classifications")
            ),
        }
        # Strip empty values so the metadata is small and unambiguous.
        lens_specific = {
            k: v for k, v in lens_specific.items() if v not in (None, "", [], {})
        }

        return NormalizedPatent(
            source=self.name,
            source_id=standard["source_id"],
            patent_number=standard["patent_number"],
            title=standard["title"],
            abstract=standard["abstract"],
            inventors=standard["inventors"],
            assignee=standard["assignee"],
            country=standard["country"],
            classification=standard["classification"],
            classification_label=standard["classification_label"],
            technology_area=standard["technology_area"],
            keywords=standard["keywords"],
            filing_date=standard["filing_date"],
            publication_date=standard["publication_date"],
            publication_year=standard["publication_year"],
            citations=standard["citations"],
            patent_family=standard["patent_family"],
            legal_status=standard["legal_status"],
            url=standard["url"],
            extra_metadata={"_lens": lens_specific},
        )

    # -- Helpers -----------------------------------------------------------

    @staticmethod
    def _format_inventors(value: Any) -> Optional[str]:
        if not value:
            return None
        if isinstance(value, str):
            return value
        names: List[str] = []
        if isinstance(value, list):
            for item in value:
                if not isinstance(item, dict):
                    continue
                name = (
                    item.get("display_name")
                    or item.get("name")
                    or " ".join(
                        filter(
                            None,
                            [
                                str(item.get("first_name") or ""),
                                str(item.get("last_name") or ""),
                            ],
                        )
                    ).strip()
                )
                if name:
                    names.append(str(name).strip())
        if not names:
            return None
        return ", ".join(names)

    @staticmethod
    def _format_applicants(value: Any) -> Optional[str]:
        if not value:
            return None
        if isinstance(value, str):
            return value
        names: List[str] = []
        if isinstance(value, list):
            for item in value:
                if not isinstance(item, dict):
                    continue
                name = (
                    item.get("display_name")
                    or item.get("name")
                    or item.get("organization")
                )
                if name:
                    names.append(str(name).strip())
        if not names:
            return None
        return ", ".join(names)

    @staticmethod
    def _collect_names(value: Any) -> List[str]:
        if not value:
            return []
        names: List[str] = []
        if isinstance(value, list):
            for item in value:
                if not isinstance(item, dict):
                    continue
                name = (
                    item.get("display_name")
                    or item.get("name")
                    or " ".join(
                        filter(
                            None,
                            [
                                str(item.get("first_name") or ""),
                                str(item.get("last_name") or ""),
                            ],
                        )
                    ).strip()
                )
                if name:
                    names.append(str(name).strip())
        return names

    @staticmethod
    def _collect_classifications(value: Any) -> List[str]:
        if not value:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            out: List[str] = []
            for item in value:
                if isinstance(item, str):
                    if item:
                        out.append(item)
                elif isinstance(item, dict):
                    symbol = (
                        item.get("symbol")
                        or item.get("code")
                        or item.get("ipc_code")
                    )
                    if symbol:
                        out.append(str(symbol))
            return out
        return []

    @staticmethod
    def _coerce_datetime(value: Any):
        from datetime import datetime, date

        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime(value.year, value.month, value.day)
        if isinstance(value, (int, float)):
            try:
                return datetime.utcfromtimestamp(float(value))
            except (OverflowError, OSError, ValueError):
                return None
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                try:
                    from dateutil import parser as _dp  # type: ignore

                    return _dp.parse(value)
                except Exception:
                    return None
        return None


__all__ = ["TheLensProvider", "DEFAULT_SINCE_DATE_PUBLISHED"]
