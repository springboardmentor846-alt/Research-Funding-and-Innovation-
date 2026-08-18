"""Asynchronous HTTP client for The Lens Patent API.

This module is the *only* component in the platform that talks to
``https://api.lens.org``.  It is intentionally low-level and provider-
agnostic — it knows about HTTP, authentication, retries, and the Lens
response envelope, but it does not know about patents, normalization, or
the database.

The Lens API is a JSON-in / JSON-out REST service.  The two endpoints
we use are:

* ``POST /lens/patent/search`` — full-text / faceted search.  Returns
  patent records with all bibliographic fields.  Supports ``from`` /
  ``size`` pagination, ``sort`` and ``include`` controls.  See
  https://docs.api.lens.org/patent/search.html.
* ``GET  /lens/patent/{lens_id}`` — fetch a single patent by its Lens
  id.  Returns the same record shape as the search endpoint.

Authentication is ``Authorization: Bearer <LENS_API_TOKEN>`` on every
request.  401/403 are treated as configuration errors and surfaced as
``LensAuthError`` so the operator can fix the token without retrying.

Rate-limiting: the Lens API returns ``429 Too Many Requests`` with a
``Retry-After`` header.  We honour that value when present, otherwise we
fall back to an exponential backoff.  We never hammer the API.

All timeouts, retries, and back-off parameters are tunable via
``PatentIntelSettings``.
"""
from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

import httpx

from app.core.logging import logger
from app.patents.core.config import patent_intel_settings


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class LensError(RuntimeError):
    """Base class for all errors raised by this client."""


class LensAuthError(LensError):
    """Raised when the Lens API rejects the bearer token."""


class LensRateLimitError(LensError):
    """Raised when we exhaust our retries against a 429 response."""

    def __init__(self, message: str, retry_after: Optional[float] = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class LensNotFoundError(LensError):
    """Raised when a lens_id is not present in the upstream corpus."""


# ---------------------------------------------------------------------------
# Configuration dataclass
# ---------------------------------------------------------------------------


@dataclass
class LensClientConfig:
    """Configuration block for the Lens HTTP client."""

    base_url: str
    token: str
    timeout_seconds: float = 30.0
    max_retries: int = 3
    backoff_seconds: float = 1.5
    page_size: int = 50
    user_agent: str = "ResearchFundingPlatform/1.0 (+lens-patent-intel)"


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class LensPatentClient:
    """Async httpx wrapper around the Lens Patent API.

    The client owns a single ``httpx.AsyncClient`` for connection pooling.
    All public methods are coroutine-safe: they never share mutable state
    across concurrent calls.

    A :class:`LensClientConfig` is required; instantiate with
    :meth:`from_settings` to read the values from
    :data:`patent_intel_settings`.
    """

    def __init__(self, config: LensClientConfig) -> None:
        if not config.token:
            raise LensAuthError(
                "LENS_API_TOKEN is not configured; cannot talk to api.lens.org"
            )
        self._config = config
        self._owns_client = True
        self._client = httpx.AsyncClient(
            base_url=config.base_url.rstrip("/"),
            timeout=httpx.Timeout(config.timeout_seconds),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            headers={
                "Authorization": f"Bearer {config.token}",
                "User-Agent": config.user_agent,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            follow_redirects=True,
        )

    # -- Construction ------------------------------------------------------

    @classmethod
    def from_settings(cls) -> "LensPatentClient":
        s = patent_intel_settings
        return cls(
            LensClientConfig(
                base_url=s.THE_LENS_BASE_URL,
                token=s.LENS_API_TOKEN,
                timeout_seconds=s.HTTP_TIMEOUT_SECONDS,
                max_retries=s.HTTP_MAX_RETRIES,
                backoff_seconds=s.HTTP_RETRY_BACKOFF_SECONDS,
                page_size=s.SYNC_PAGE_SIZE,
                user_agent=s.HTTP_USER_AGENT,
            )
        )

    # -- Lifecycle ---------------------------------------------------------

    async def aclose(self) -> None:
        try:
            await self._client.aclose()
        except Exception:  # pragma: no cover - shutdown best-effort
            pass

    async def __aenter__(self) -> "LensPatentClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    # -- Search ------------------------------------------------------------

    async def search(
        self,
        *,
        query: str = "*",
        from_offset: int = 0,
        size: Optional[int] = None,
        sort: Optional[Sequence[Mapping[str, str]]] = None,
        include: Optional[Sequence[str]] = None,
        filters: Optional[Sequence[Mapping[str, Any]]] = None,
    ) -> "LensSearchResult":
        """Call ``POST /lens/patent/search`` and return the parsed envelope.

        Parameters
        ----------
        query:
            A Lens query string.  ``"*"`` matches every document.
        from_offset:
            Zero-based offset of the first hit to return (the Lens ``from``
            parameter).  Used for paginated reads.
        size:
            Number of hits to request for this page.  Defaults to
            ``config.page_size``.
        sort:
            Optional sort spec; each entry is a ``{"field": "..."}`` dict.
            Defaults to descending publication date so the most recent
            records surface first.
        include:
            Optional list of fields to return.  Defaults to a curated set
            that covers everything the dashboard needs.
        filters:
            Optional list of filter clauses to AND onto the query.
            Each entry is a dict like
            ``{"field": "jurisdiction", "operator": "=", "value": "US"}``.
        """
        payload = self._build_search_payload(
            query=query,
            from_offset=from_offset,
            size=size or self._config.page_size,
            sort=sort,
            include=include,
            filters=filters,
        )
        envelope = await self._post_json("/patent/search", payload)
        return self._parse_search_envelope(envelope)

    async def search_iter(
        self,
        *,
        query: str = "*",
        page_size: Optional[int] = None,
        sort: Optional[Sequence[Mapping[str, str]]] = None,
        include: Optional[Sequence[str]] = None,
        filters: Optional[Sequence[Mapping[str, Any]]] = None,
        max_pages: int = 50,
    ) -> "LensSearchIterator":
        """Return an async iterator over every hit of a search.

        The iterator handles pagination for callers; it stops when the
        upstream exhausts the result set or after ``max_pages`` pages
        (whichever comes first).
        """
        return LensSearchIterator(
            client=self,
            query=query,
            page_size=page_size or self._config.page_size,
            sort=sort,
            include=include,
            filters=filters,
            max_pages=max_pages,
        )

    async def get_patent(self, lens_id: str) -> Dict[str, Any]:
        """Fetch a single patent by Lens id from ``GET /lens/patent/{id}``."""
        if not lens_id:
            raise LensError("lens_id is required")
        path = f"/patent/{lens_id}"
        try:
            response = await self._client.get(path)
        except httpx.TimeoutException as exc:
            raise LensError(f"timeout fetching patent {lens_id}: {exc}") from exc
        except httpx.HTTPError as exc:
            raise LensError(f"HTTP error fetching patent {lens_id}: {exc}") from exc
        if response.status_code == 404:
            raise LensNotFoundError(f"lens_id {lens_id!r} not found in upstream")
        if response.status_code in (401, 403):
            raise LensAuthError(
                f"authentication failed (status {response.status_code}); "
                "check LENS_API_TOKEN"
            )
        try:
            return response.json()
        except ValueError as exc:
            raise LensError(f"non-JSON response for {lens_id}: {exc}") from exc

    # -- Request core ------------------------------------------------------

    def _build_search_payload(
        self,
        *,
        query: str,
        from_offset: int,
        size: int,
        sort: Optional[Sequence[Mapping[str, str]]],
        include: Optional[Sequence[str]],
        filters: Optional[Sequence[Mapping[str, Any]]],
    ) -> Dict[str, Any]:
        if sort is None:
            # Newest first so the dashboard and incremental sync always
            # prefer the most recent records.
            sort = [{"date_published": "desc"}]
        if include is None:
            include = [
                "lens_id",
                "publication_type",
                "jurisdiction",
                "kind",
                "abstract",
            ]
        must: List[Dict[str, Any]] = []
        if query and query != "*":
            must.append({"match": {"free_text": query}})
        if filters:
            for f in filters:
                must.append(dict(f))
        if must:
            where = {"bool": {"must": must}}
        else:
            where = {"match_all": {}}
        return {
            "query": where,
            "from": int(from_offset),
            "size": int(size),
            "sort": list(sort),
            "include": list(include),
        }

    async def _post_json(
        self, path: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        attempt = 0
        last_exc: Optional[Exception] = None
        while attempt <= self._config.max_retries:
            attempt += 1
            started = time.perf_counter()
            try:
                logger.info(
                    "[lens-client] POST {} headers={{auth=present, content-type=application/json}} payload={}",
                    path,
                    json.dumps(payload, separators=(",", ":"))[:2000],
                )
                response = await self._client.post(path, json=payload)
            except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError) as exc:
                last_exc = exc
                if attempt > self._config.max_retries:
                    break
                delay = self._backoff(attempt)
                logger.warning(
                    f"[lens-client] {exc.__class__.__name__} on POST {path} "
                    f"(attempt {attempt}/{self._config.max_retries}); "
                    f"retrying in {delay:.1f}s"
                )
                await asyncio.sleep(delay)
                continue

            elapsed_ms = (time.perf_counter() - started) * 1000.0
            logger.info(
                "[lens-client] response status={} elapsed_ms={:.1f} path={} body={}",
                response.status_code,
                elapsed_ms,
                path,
                response.text[:4000],
            )
            if response.status_code == 401 or response.status_code == 403:
                raise LensAuthError(
                    f"authentication failed (status {response.status_code}); "
                    "check LENS_API_TOKEN"
                )
            if response.status_code == 429:
                retry_after = self._parse_retry_after(response)
                if attempt > self._config.max_retries:
                    raise LensRateLimitError(
                        f"rate limited (status 429) on POST {path} after "
                        f"{attempt - 1} retries",
                        retry_after=retry_after,
                    )
                delay = retry_after if retry_after is not None else self._backoff(attempt)
                logger.warning(
                    f"[lens-client] 429 on POST {path} "
                    f"(attempt {attempt}/{self._config.max_retries}); "
                    f"retrying in {delay:.1f}s"
                )
                await asyncio.sleep(delay)
                continue
            if response.status_code >= 500:
                if attempt > self._config.max_retries:
                    raise LensError(
                        f"server error (status {response.status_code}) on "
                        f"POST {path} after {attempt - 1} retries"
                    )
                delay = self._backoff(attempt)
                logger.warning(
                    f"[lens-client] {response.status_code} on POST {path} "
                    f"(attempt {attempt}/{self._config.max_retries}); "
                    f"retrying in {delay:.1f}s"
                )
                await asyncio.sleep(delay)
                continue

            # 2xx — success
            try:
                return response.json()
            except ValueError as exc:
                raise LensError(
                    f"non-JSON success response on POST {path}: {exc}"
                ) from exc

        if last_exc is not None:
            raise LensError(f"request failed after retries: {last_exc}") from last_exc
        raise LensError(f"request failed after retries on POST {path}")

    @staticmethod
    def _backoff(attempt: int) -> float:
        """Exponential backoff with a 60s cap."""
        return min(60.0, 1.5 * (2 ** (attempt - 1)))

    @staticmethod
    def _parse_retry_after(response: httpx.Response) -> Optional[float]:
        header = response.headers.get("Retry-After")
        if not header:
            return None
        try:
            return float(header)
        except ValueError:
            return None

    def _parse_search_envelope(self, envelope: Any) -> "LensSearchResult":
        if not isinstance(envelope, dict):
            raise LensError(
                f"unexpected search response shape: {type(envelope).__name__}"
            )
        # Lens returns a top-level ``data`` array and a ``total`` field
        # when ``include`` is set.  The legacy envelope had ``results``.
        records: List[Dict[str, Any]] = []
        if isinstance(envelope.get("data"), list):
            records = [r for r in envelope["data"] if isinstance(r, dict)]
        elif isinstance(envelope.get("results"), list):
            records = [r for r in envelope["results"] if isinstance(r, dict)]

        total: Optional[int] = None
        if "total" in envelope:
            try:
                total = int(envelope["total"])
            except (TypeError, ValueError):
                total = None
        if total is None and records and isinstance(envelope.get("count"), int):
            total = int(envelope["count"])
        return LensSearchResult(records=records, total=total, raw=envelope)


# ---------------------------------------------------------------------------
# Pagination iterator
# ---------------------------------------------------------------------------


@dataclass
class LensSearchResult:
    """A single page of search results."""

    records: List[Dict[str, Any]]
    total: Optional[int] = None
    raw: Dict[str, Any] = field(default_factory=dict)


class LensSearchIterator:
    """Async iterator that walks every page of a Lens search."""

    def __init__(
        self,
        *,
        client: LensPatentClient,
        query: str,
        page_size: int,
        sort: Optional[Sequence[Mapping[str, str]]],
        include: Optional[Sequence[str]],
        filters: Optional[Sequence[Mapping[str, Any]]],
        max_pages: int,
    ) -> None:
        self._client = client
        self._query = query
        self._size = max(1, int(page_size))
        self._sort = sort
        self._include = include
        self._filters = filters
        self._max_pages = max(1, int(max_pages))
        self._offset = 0
        self._pages_returned = 0
        self._exhausted = False

    def __aiter__(self) -> "LensSearchIterator":
        return self

    async def __anext__(self) -> LensSearchResult:
        if self._exhausted or self._pages_returned >= self._max_pages:
            raise StopAsyncIteration
        result = await self._client.search(
            query=self._query,
            from_offset=self._offset,
            size=self._size,
            sort=self._sort,
            include=self._include,
            filters=self._filters,
        )
        self._pages_returned += 1
        if not result.records:
            self._exhausted = True
            raise StopAsyncIteration
        self._offset += len(result.records)
        if result.total is not None and self._offset >= result.total:
            self._exhausted = True
        elif len(result.records) < self._size:
            # The server returned a partial page — nothing more to fetch.
            self._exhausted = True
        return result


# ---------------------------------------------------------------------------
# Convenience helpers (keyword / domain / inventor / assignee search)
# ---------------------------------------------------------------------------


class LensSearchFilters:
    """Builder for the most common Lens filter shapes.

    These helpers exist so the rest of the platform can request the
    common search patterns (keyword, technology domain, inventor,
    assignee) without having to hand-roll filter dicts.
    """

    @staticmethod
    def keyword(text: str) -> Sequence[Mapping[str, Any]]:
        """Free-text keyword search across title / abstract / claims."""
        if not text:
            return []
        return [{"match": {"free_text": text}}]

    @staticmethod
    def technology_domain(
        *,
        cpc: Optional[str] = None,
        ipc: Optional[str] = None,
    ) -> List[Mapping[str, Any]]:
        """Filter by a CPC or IPC classification prefix."""
        clauses: List[Mapping[str, Any]] = []
        if cpc:
            clauses.append({"prefix": {"cpc_classifications.symbol": cpc}})
        if ipc:
            clauses.append({"prefix": {"ipc_classifications.symbol": ipc}})
        return clauses

    @staticmethod
    def inventor(name: str) -> Sequence[Mapping[str, Any]]:
        """Match an inventor by display name (case-insensitive)."""
        if not name:
            return []
        return [
            {
                "nested": {
                    "path": "inventors",
                    "query": {"match": {"inventors.display_name": name}},
                }
            }
        ]

    @staticmethod
    def assignee(name: str) -> Sequence[Mapping[str, Any]]:
        """Match an applicant / assignee by display name (case-insensitive)."""
        if not name:
            return []
        return [
            {
                "nested": {
                    "path": "applicants",
                    "query": {"match": {"applicants.display_name": name}},
                }
            }
        ]

    @staticmethod
    def inventor_id(lens_inventor_id: str) -> Sequence[Mapping[str, Any]]:
        """Match by the Lens internal inventor id."""
        if not lens_inventor_id:
            return []
        return [
            {
                "nested": {
                    "path": "inventors",
                    "query": {"term": {"inventors.lens_id": lens_inventor_id}},
                }
            }
        ]

    @staticmethod
    def assignee_id(lens_applicant_id: str) -> Sequence[Mapping[str, Any]]:
        """Match by the Lens internal applicant id."""
        if not lens_applicant_id:
            return []
        return [
            {
                "nested": {
                    "path": "applicants",
                    "query": {"term": {"applicants.lens_id": lens_applicant_id}},
                }
            }
        ]

    @staticmethod
    def country(jurisdiction: str) -> Sequence[Mapping[str, Any]]:
        if not jurisdiction:
            return []
        return [{"term": {"jurisdiction": jurisdiction.upper()}}]

    @staticmethod
    def year_range(
        *, start: Optional[int] = None, end: Optional[int] = None
    ) -> List[Mapping[str, Any]]:
        if start is None and end is None:
            return []
        rng: Dict[str, Any] = {}
        if start is not None:
            rng["gte"] = int(start)
        if end is not None:
            rng["lte"] = int(end)
        return [{"range": {"year_published": rng}}]

    @staticmethod
    def combine(*clauses: Iterable[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
        """Flatten and dedupe a list of filter clauses."""
        out: List[Mapping[str, Any]] = []
        for c in clauses:
            for clause in c or []:
                if clause not in out:
                    out.append(clause)
        return out


__all__ = [
    "LensAuthError",
    "LensClientConfig",
    "LensError",
    "LensNotFoundError",
    "LensPatentClient",
    "LensRateLimitError",
    "LensSearchFilters",
    "LensSearchIterator",
    "LensSearchResult",
]
