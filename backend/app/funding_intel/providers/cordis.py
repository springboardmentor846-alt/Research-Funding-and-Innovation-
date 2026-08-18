"""CORDIS provider (EU research projects).

Endpoint:
    GET https://cordis.europa.eu/api/search?q=*&type=/project&format=json&page=1,items_per_page=50

CORDIS exposes a Solr-style search API at ``/api/search``. Results are
paginated via the ``page`` parameter and the response wraps hits in
``payload``/``hits`` arrays. ``hitsPerPage``/``totalResults`` are
returned as integers.

Authentication: none (public API).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

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
class CORDISProvider(BaseProvider):
    """Adapter for the CORDIS ``/api/search`` EU projects endpoint."""

    name = "cordis"

    def __init__(self) -> None:
        super().__init__(name=self.name)
        s = funding_intel_settings
        self._client: Optional[ProviderHTTPClient] = None
        self._base_url = s.CORDIS_BASE_URL
        # CORDIS caps items_per_page at 100 in practice.
        self._page_size = min(s.SYNC_PAGE_SIZE, 100)

    async def initialize(self) -> None:
        if self._client is not None:
            return
        self._client = ProviderHTTPClient(
            name=self.name,
            base_url=self._base_url,
        )
        logger.info(f"[{self.name}] HTTP client initialised against {self._base_url}")

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def fetch_batch(
        self,
        *,
        cursor: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> ProviderBatch:
        if self._client is None:
            await self.initialize()

        # Cursor: "<page>:<items_per_page>"
        page = 1
        per_page = page_size or self._page_size
        if cursor:
            try:
                head, tail = cursor.split(":", 1)
                page = int(head or 1)
                per_page = int(tail or per_page)
            except (ValueError, AttributeError):
                page = 1

        params: Dict[str, Any] = {
            "q": "*",
            "type": "/project",
            "format": "json",
            "page": page,
            "items_per_page": per_page,
        }

        started = __import__("time").perf_counter()
        try:
            data = await self._client.get_json("/search", params=params)
        except Exception as exc:
            self._record_failure(str(exc))
            raise ProviderError(f"CORDIS request failed: {exc}") from exc
        elapsed_ms = (__import__("time").perf_counter() - started) * 1000.0
        self._record_success(elapsed_ms)

        payload = data.get("payload") if isinstance(data, dict) else None
        if not isinstance(payload, dict):
            payload = {}

        hits = payload.get("hits") or payload.get("hit") or []
        if not isinstance(hits, list):
            hits = []

        next_cursor = f"{page + 1}:{per_page}" if hits else None
        return ProviderBatch(records=hits, next_cursor=next_cursor, total_estimated=payload.get("totalResults"))

    def normalize(self, raw: Dict[str, Any]) -> Optional[NormalizedFunding]:
        if not isinstance(raw, dict):
            return None

        # CORDIS's content model varies; try a few common shapes.
        proj = raw.get("project") or raw.get("content") or raw
        if not isinstance(proj, dict):
            return None

        # Resolve project_id safely (explicit parens avoid Python's ternary
        # precedence trap with chained ``or``).
        project_id = (
            proj.get("id")
            or proj.get("projectId")
            or proj.get("reference")
        )
        if not project_id:
            metadata = proj.get("metadata")
            if isinstance(metadata, dict):
                project_id = metadata.get("id")
        if not project_id:
            return None

        title_obj = proj.get("title") or {}
        if isinstance(title_obj, dict):
            title = title_obj.get("en") or next(iter(title_obj.values()), None)
        else:
            title = title_obj
        title = (str(title) if title else "").strip()
        if not title:
            return None

        desc_obj = proj.get("objective") or proj.get("abstract") or proj.get("description")
        if isinstance(desc_obj, dict):
            description = desc_obj.get("en") or next(iter(desc_obj.values()), None)
        else:
            description = desc_obj

        # Organisation
        coord = proj.get("coordinator") or {}
        if isinstance(coord, dict):
            org = coord.get("name") or coord.get("organisation")
            country = coord.get("country") or (coord.get("address") or {}).get("country") if isinstance(coord.get("address"), dict) else None
        else:
            org = None
            country = None

        # Programme / funding
        programme = proj.get("programme") or proj.get("frameworkProgramme") or "EU Framework Programme"
        funding_scheme = proj.get("fundingScheme") or proj.get("scheme")
        status = (proj.get("status") or "active").lower()

        # Money
        ec_max_contribution = self._as_float(proj.get("ecMaxContribution") or proj.get("totalCost"))
        ec_contribution = self._as_float(proj.get("ecContribution") or proj.get("euContribution"))

        # Dates
        start = self._parse_date(proj.get("startDate") or proj.get("start"))
        end = self._parse_date(proj.get("endDate") or proj.get("end"))
        last_update = self._parse_date(proj.get("lastUpdate") or proj.get("lastUpdateDate"))

        return NormalizedFunding(
            source=self.name,
            source_id=str(project_id),
            title=title[:500],
            description=(str(description) if description else title)[:8000],
            agency=programme if isinstance(programme, str) else None,
            organization=org,
            country=country,
            category=funding_scheme if isinstance(funding_scheme, str) else None,
            research_area=programme if isinstance(programme, str) else None,
            funding_type="grant",
            keywords=proj.get("keywords"),
            eligibility=proj.get("eligibility"),
            currency="EUR",
            funding_amount=ec_max_contribution or ec_contribution,
            minimum_amount=ec_contribution,
            maximum_amount=ec_max_contribution,
            deadline=end,
            posted_date=start,
            status="open" if status in ("active", "ongoing", "open") else "closed",
            source_url=f"https://cordis.europa.eu/project/id/{project_id}",
            last_updated=last_update,
            extra_metadata={
                "framework_programme": programme,
                "funding_scheme": funding_scheme,
                "coordinator": org,
                "coordinator_country": country,
            },
        )

    @staticmethod
    def _parse_date(value: Any) -> Optional[datetime]:
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        s = str(value).strip()
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ"):
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
