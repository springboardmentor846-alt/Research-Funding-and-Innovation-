"""Grants.gov provider.

Endpoint:
    POST https://api.grants.gov/v1/api/search2

Authentication: none for search2; the API is public.
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
class GrantsGovProvider(BaseProvider):
    """Adapter for the Grants.gov ``search2`` opportunity API."""

    name = "grants_gov"

    def __init__(self) -> None:
        super().__init__(name=self.name)
        s = funding_intel_settings
        self._client: Optional[ProviderHTTPClient] = None
        self._base_url = s.GRANTSGOV_BASE_URL
        self._page_size = min(s.SYNC_PAGE_SIZE, 100)  # Grants.gov caps at 100

    async def initialize(self) -> None:
        if self._client is not None:
            return
        self._client = ProviderHTTPClient(
            name=self.name,
            base_url=self._base_url,
            headers={"Content-Type": "application/json"},
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

        # Cursor: "<start>:<rows>"
        start = 0
        rows = page_size or self._page_size
        if cursor:
            try:
                start = int(cursor.split(":", 1)[0] or 0)
            except (ValueError, AttributeError):
                start = 0

        payload: Dict[str, Any] = {
            "rows": rows,
            "start": start,
            # Search the open and forecasted universes by default
            "oppStatuses": "open|forecasted",
        }

        started = __import__("time").perf_counter()
        try:
            data = await self._client.post_json("/search2", json=payload)
        except Exception as exc:
            self._record_failure(str(exc))
            raise ProviderError(f"Grants.gov request failed: {exc}") from exc
        elapsed_ms = (__import__("time").perf_counter() - started) * 1000.0
        self._record_success(elapsed_ms)

        # Grants.gov returns either {"data": {...}} or a top-level dict.
        wrapper = data.get("data") if isinstance(data, dict) and "data" in data else data
        opps: List[Dict[str, Any]] = []
        hit_count: Optional[int] = None
        if isinstance(wrapper, dict):
            opps = wrapper.get("oppHits") or wrapper.get("opportunities") or []
            hit_count = wrapper.get("hitCount")
        elif isinstance(wrapper, list):
            opps = wrapper

        # Stop paging when we have walked past the total available records.
        next_start = start + len(opps)
        exhausted = (
            not opps
            or next_start >= (hit_count or 0)
            or len(opps) < rows
        )
        next_cursor = None if exhausted else f"{next_start}:{rows}"
        return ProviderBatch(
            records=opps,
            next_cursor=next_cursor,
            total_estimated=hit_count,
        )

    def normalize(self, raw: Dict[str, Any]) -> Optional[NormalizedFunding]:
        if not isinstance(raw, dict):
            return None

        opp_id = raw.get("id") or raw.get("opportunityId")
        if not opp_id:
            return None

        title = (raw.get("title") or raw.get("opportunityTitle") or "").strip()
        if not title:
            return None

        description = (
            raw.get("description")
            or raw.get("synopsis")
            or raw.get("descriptionText")
            or ""
        ).strip()

        agency = raw.get("agency") or raw.get("owningAgency") or raw.get("department")
        category = raw.get("category") or raw.get("fundingCategory")
        funding_type = (raw.get("fundingInstrumentType") or raw.get("opportunityCategory") or "grant")
        if isinstance(funding_type, list):
            funding_type = ", ".join(str(x) for x in funding_type) or "grant"

        # Amounts
        award_ceiling = raw.get("awardCeiling") or raw.get("awardMax")
        award_floor = raw.get("awardFloor") or raw.get("awardMin")
        award_ceiling = self._as_float(award_ceiling)
        award_floor = self._as_float(award_floor)

        # Dates
        close_date = self._parse_date(raw.get("closeDate") or raw.get("closeDateExplanation"))
        posted_date = self._parse_date(raw.get("postDate") or raw.get("createdAt"))

        # Status
        status_raw = (raw.get("oppStatus") or raw.get("status") or "").lower()
        if "close" in status_raw:
            status = "closed"
        elif "forecast" in status_raw:
            status = "forecast"
        else:
            status = "open"

        # Keywords
        keyword_field = raw.get("keyword") or raw.get("keywords")
        if isinstance(keyword_field, list):
            keywords = ", ".join(str(k) for k in keyword_field if k)
        else:
            keywords = str(keyword_field) if keyword_field else None

        # Eligibility
        elig = raw.get("eligibleApplicants") or raw.get("applicantTypes")
        if isinstance(elig, list):
            elig = ", ".join(str(x) for x in elig if x)

        return NormalizedFunding(
            source=self.name,
            source_id=str(opp_id),
            title=title[:500],
            description=(description or title)[:8000],
            agency=agency,
            organization=agency,
            country="United States",
            category=category,
            research_area=category,
            funding_type=str(funding_type).lower(),
            keywords=keywords,
            eligibility=str(elig) if elig else None,
            currency="USD",
            minimum_amount=award_floor,
            maximum_amount=award_ceiling,
            funding_amount=award_ceiling,
            deadline=close_date,
            posted_date=posted_date,
            status=status,
            source_url=raw.get("link") or raw.get("opportunityUrl") or raw.get("url"),
            last_updated=self._parse_date(raw.get("lastUpdatedDate")),
            extra_metadata={
                "cfda": raw.get("cfda") or raw.get("cfdaNumber"),
                "opp_number": raw.get("number") or raw.get("opportunityNumber"),
                "cost_sharing": raw.get("costSharing"),
            },
        )

    @staticmethod
    def _parse_date(value: Any) -> Optional[datetime]:
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        s = str(value).strip()
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%m/%d/%Y"):
            try:
                return datetime.strptime(s.replace("Z", ""), fmt)
            except ValueError:
                continue
        return None

    @staticmethod
    def _as_float(value: Any) -> Optional[float]:
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
