"""OpenAlex provider.

Endpoint:
    GET https://api.openalex.org/works
        ?search=grant%20funding&filter=type:grant,language:en&per-page=200&page=1

OpenAlex exposes ``/works`` (research outputs) and ``/funders``. We use
``/works`` filtered to ``type:grant`` so that grant/funding
opportunities are surfaced. ``/funders`` is used in a secondary pass to
discover funder metadata and construct organisation fields.

Authentication
--------------
OpenAlex is unauthenticated but recommends a "polite pool" identifier:
the API key (when provided) is sent as the ``api_key`` query parameter
and the operator email as ``mailto``. See
https://docs.openalex.org/.

Pagination
----------
``per_page`` is capped at 200 by the upstream. We use the
``meta.count`` value to compute the page range.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

from app.core.logging import logger
from app.funding_intel.core.base import (
    BaseProvider,
    NormalizedFunding,
    ProviderBatch,
    ProviderError,
)
from app.funding_intel.core.config import funding_intel_settings
from app.funding_intel.core.http_client import ProviderHTTPClient
from app.funding_intel.core.registry import register_provider


@register_provider
class OpenAlexProvider(BaseProvider):
    """Adapter for the OpenAlex ``/works?type=grant`` feed."""

    name = "openalex"

    def __init__(self) -> None:
        super().__init__(name=self.name)
        s = funding_intel_settings
        self._client: Optional[ProviderHTTPClient] = None
        self._base_url = s.OPENALEX_BASE_URL
        self._api_key = (s.OPENALEX_API_KEY or "").strip()
        self._mailto = (s.OPENALEX_MAILTO or "").strip()
        # OpenAlex caps ``per_page`` at 200.
        self._page_size = min(s.SYNC_PAGE_SIZE, 200)
        # Funder cache: id -> display_name, populated lazily.
        self._funder_cache: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    async def initialize(self) -> None:
        if self._client is not None:
            return
        # OpenAlex's polite-pool key is sent as a query parameter, not
        # a header, so we set a friendlier User-Agent instead.
        headers = {
            "User-Agent": f"ResearchFundingPlatform/1.0 (mailto:{self._mailto})"
            if self._mailto
            else "ResearchFundingPlatform/1.0 (+funding-intel)"
        }
        self._client = ProviderHTTPClient(
            name=self.name,
            base_url=self._base_url,
            headers=headers,
        )
        logger.info(
            f"[{self.name}] HTTP client initialised against {self._base_url} "
            f"(api_key={'yes' if self._api_key else 'no'}, mailto={self._mailto or '-'})"
        )

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        self._funder_cache.clear()

    # ------------------------------------------------------------------
    # Fetch
    # ------------------------------------------------------------------
    async def fetch_batch(
        self,
        *,
        cursor: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> ProviderBatch:
        if self._client is None:
            await self.initialize()

        # Cursor: "<page>"
        page = 1
        if cursor:
            try:
                page = int(cursor.split(":", 1)[0] or 1)
            except (ValueError, AttributeError):
                page = 1

        per_page = page_size or self._page_size

        # Filter to grant-type works; ``type:grant`` is the OpenAlex
        # identifier for funding/grants. ``language:en`` keeps the
        # payload small.
        params: Dict[str, Any] = {
            "filter": "type:grant,language:en",
            "per-page": per_page,
            "page": page,
            "sort": "publication_date:desc",
        }
        if self._api_key:
            params["api_key"] = self._api_key
        if self._mailto:
            params["mailto"] = self._mailto

        started = __import__("time").perf_counter()
        try:
            data = await self._client.get_json("/works", params=params)
        except Exception as exc:
            self._record_failure(str(exc))
            raise ProviderError(f"OpenAlex request failed: {exc}") from exc
        elapsed_ms = (__import__("time").perf_counter() - started) * 1000.0
        self._record_success(elapsed_ms)

        results: List[Dict[str, Any]] = []
        if isinstance(data, dict):
            results = data.get("results") or []
            meta = data.get("meta") or {}
            total = meta.get("count")
        else:
            total = None

        # OpenAlex exposes the next cursor via meta; otherwise page+1.
        next_cursor = f"{page + 1}" if results and (total is None or page * per_page < total) else None
        return ProviderBatch(records=results, next_cursor=next_cursor, total_estimated=total)

    # ------------------------------------------------------------------
    # Normalize
    # ------------------------------------------------------------------
    def normalize(self, raw: Dict[str, Any]) -> Optional[NormalizedFunding]:
        if not isinstance(raw, dict):
            return None

        openalex_id = raw.get("id")
        if not openalex_id:
            return None
        # OpenAlex IDs are URLs of the form "https://openalex.org/W..."
        source_id = str(openalex_id).rsplit("/", 1)[-1]

        title = (raw.get("title") or "").strip()
        if not title:
            return None
        # Strip the leading "Re: " or "Grant - " that OpenAlex sometimes adds.
        if title.lower().startswith("re: "):
            title = title[4:].strip()

        # Abstract: OpenAlex returns an inverted-index string. We render
        # it as best-effort plain text.
        description = self._render_abstract(raw.get("abstract_inverted_index"), title)

        # Funder(s)
        funders = raw.get("funders") or []
        funder_name: Optional[str] = None
        funder_id: Optional[str] = None
        if isinstance(funders, list) and funders:
            first = funders[0] or {}
            if isinstance(first, dict):
                funder_name = first.get("display_name")
                funder_id = first.get("id")

        # Author/host institution
        host_inst = raw.get("host_venue") or {}
        host_name = (host_inst or {}).get("display_name") if isinstance(host_inst, dict) else None
        authorships = raw.get("authorships") or []
        primary_org = None
        if isinstance(authorships, list) and authorships:
            insts = (authorships[0] or {}).get("institutions") or []
            if isinstance(insts, list) and insts and isinstance(insts[0], dict):
                primary_org = insts[0].get("display_name")

        # Dates
        pub_date = self._parse_date(raw.get("publication_date"))
        posted_date = pub_date
        # OpenAlex doesn't expose a "deadline"; use grant end date or None.
        end_date = self._parse_date(raw.get("end_date"))
        deadline = end_date

        # Funding: OpenAlex awards are stored under ``awards``.
        awards = raw.get("awards") or []
        amount: Optional[float] = None
        currency = "USD"
        if isinstance(awards, list) and awards:
            aw = awards[0] or {}
            if isinstance(aw, dict):
                amount = self._as_float(aw.get("amount"))
                currency = aw.get("currency") or "USD"

        # Keywords / concepts
        keywords = self._collect_keywords(raw)
        concept_names = self._collect_concepts(raw)
        research_area = ", ".join(concept_names[:3]) if concept_names else None

        # Country
        country = self._resolve_country(raw, funder_name)

        # Type
        funding_type = "grant"
        raw_type = (raw.get("type") or "").lower()
        if "fellowship" in (raw.get("display_name") or "").lower():
            funding_type = "fellowship"

        return NormalizedFunding(
            source=self.name,
            source_id=source_id,
            title=title[:500],
            description=(description or title)[:8000],
            agency=funder_name,
            organization=primary_org or host_name or funder_name,
            country=country,
            category=raw_type or "grant",
            research_area=research_area,
            funding_type=funding_type,
            keywords=keywords,
            eligibility=None,
            funding_amount=amount,
            currency=currency,
            minimum_amount=amount,
            maximum_amount=amount,
            deadline=deadline,
            posted_date=posted_date,
            status="open",  # OpenAlex grant records are published opportunities
            source_url=raw.get("doi") or f"https://openalex.org/{source_id}",
            last_updated=self._parse_date(raw.get("updated_date")) or pub_date,
            extra_metadata={
                "openalex_id": str(openalex_id),
                "doi": raw.get("doi"),
                "funder_id": funder_id,
                "primary_organization": primary_org,
                "host_venue": host_name,
                "language": raw.get("language"),
                "is_oa": raw.get("open_access", {}).get("is_oa") if isinstance(raw.get("open_access"), dict) else None,
                "cited_by_count": raw.get("cited_by_count"),
                "publication_year": raw.get("publication_year"),
            },
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _render_abstract(inv_index: Any, fallback: str) -> str:
        if not inv_index or not isinstance(inv_index, dict):
            return fallback
        try:
            words: List[tuple[int, str]] = []
            for word, positions in inv_index.items():
                if not isinstance(positions, list):
                    continue
                for p in positions:
                    words.append((int(p), word))
            if not words:
                return fallback
            words.sort(key=lambda x: x[0])
            return " ".join(w for _, w in words)
        except Exception:
            return fallback

    @staticmethod
    def _parse_date(value: Any) -> Optional[datetime]:
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        s = str(value).strip()
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m"):
            try:
                return datetime.strptime(s.replace("Z", ""), fmt)
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _as_float(value: Any) -> Optional[float]:
        if value is None or value == "":
            return None
        try:
            return float(str(value).replace(",", ""))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _collect_keywords(raw: Dict[str, Any]) -> Optional[str]:
        keywords = raw.get("keywords") or []
        if isinstance(keywords, list):
            names = [k.get("display_name") for k in keywords if isinstance(k, dict) and k.get("display_name")]
            return ", ".join(n for n in names if n) or None
        if isinstance(keywords, str):
            return keywords
        return None

    @staticmethod
    def _collect_concepts(raw: Dict[str, Any]) -> List[str]:
        concepts = raw.get("concepts") or []
        names: List[str] = []
        if isinstance(concepts, list):
            for c in concepts[:5]:
                if isinstance(c, dict) and c.get("display_name"):
                    names.append(c["display_name"])
        return names

    @staticmethod
    def _resolve_country(raw: Dict[str, Any], funder_name: Optional[str]) -> Optional[str]:
        # Try funders -> country_code first
        funders = raw.get("funders") or []
        if isinstance(funders, list) and funders:
            for f in funders:
                if isinstance(f, dict) and f.get("country_code"):
                    return f.get("country_code")
        # Fall back to authorships institutions
        for a in raw.get("authorships") or []:
            if not isinstance(a, dict):
                continue
            for inst in a.get("institutions") or []:
                if isinstance(inst, dict) and inst.get("country_code"):
                    return inst.get("country_code")
        return None


__all__ = ["OpenAlexProvider"]
