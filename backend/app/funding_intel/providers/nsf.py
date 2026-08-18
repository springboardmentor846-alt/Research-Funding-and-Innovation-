"""NSF Award Search provider.

Endpoint:
    GET https://api.nsf.gov/services/v1/awards.json
        ?keyword=...&fundProgramName=...&startDate=...&rpp=25&page=1

NSF's public ``awards.json`` endpoint does not require authentication.
The API is paginated via ``page`` and capped at 25 records per page
when ``rpp=25`` (the default max).

Authentication: none.
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
class NSFProvider(BaseProvider):
    """Adapter for the NSF ``services/v1/awards.json`` API."""

    name = "nsf"

    def __init__(self) -> None:
        super().__init__(name=self.name)
        s = funding_intel_settings
        self._client: Optional[ProviderHTTPClient] = None
        self._base_url = s.NSF_BASE_URL
        self._page_size = min(s.SYNC_PAGE_SIZE, 25)  # NSF caps at 25

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

        # Cursor: "<page>:<rpp>"
        page = 1
        rpp = page_size or self._page_size
        if cursor:
            try:
                head, tail = cursor.split(":", 1)
                page = int(head or 1)
                rpp = int(tail or rpp)
            except (ValueError, AttributeError):
                page = 1

        params: Dict[str, Any] = {
            "rpp": rpp,
            "page": page,
            # Filter to recent years to keep payload focused on active programs
            "fundProgramName": "",
        }

        started = __import__("time").perf_counter()
        try:
            data = await self._client.get_json("/awards.json", params=params)
        except Exception as exc:
            self._record_failure(str(exc))
            raise ProviderError(f"NSF request failed: {exc}") from exc
        elapsed_ms = (__import__("time").perf_counter() - started) * 1000.0
        self._record_success(elapsed_ms)

        response = data.get("response") if isinstance(data, dict) else None
        awards = (response or {}).get("award") or []
        # NSF's metadata block uses totalCount
        total = None
        metadata = data.get("metadata") if isinstance(data, dict) else None
        if isinstance(metadata, dict):
            total = metadata.get("totalCount")

        next_cursor = f"{page + 1}:{rpp}" if awards else None
        return ProviderBatch(records=awards, next_cursor=next_cursor, total_estimated=total)

    def normalize(self, raw: Dict[str, Any]) -> Optional[NormalizedFunding]:
        if not isinstance(raw, dict):
            return None

        award_id = raw.get("id") or raw.get("awardeeName")
        if not raw.get("title") or not raw.get("id"):
            return None
        award_id = str(raw.get("id"))

        title = (raw.get("title") or "").strip()
        abstract = (raw.get("abstractText") or raw.get("description") or "").strip()
        pi = raw.get("piFirstName", "") + " " + raw.get("piLastName", "")
        pi = pi.strip() or None
        awardee = raw.get("awardeeName")

        # Amount
        amount = self._as_float(raw.get("fundProgramName") and raw.get("estimatedTotalAmt"))
        amount = self._as_float(raw.get("estimatedTotalAmt") or raw.get("amt") or raw.get("fundAmount"))
        min_amt = self._as_float(raw.get("fundObligatedAmt"))
        max_amt = amount

        # Dates
        start_date = self._parse_date(raw.get("startDate") or raw.get("awardEffectiveDate"))
        exp_date = self._parse_date(raw.get("expDate") or raw.get("expiredDate"))

        # Organization
        org = awardee
        program = raw.get("fundProgramName")
        directorate = raw.get("dir") or raw.get("directorate")
        research_area = ", ".join([p for p in (program, directorate) if p]) or program

        return NormalizedFunding(
            source=self.name,
            source_id=award_id,
            title=title[:500],
            description=(abstract or title)[:8000],
            agency=raw.get("agency") or "NSF",
            organization=org,
            country="United States",
            category=program,
            research_area=research_area,
            funding_type="grant",
            keywords=raw.get("keyword") or None,
            eligibility=pi,
            currency="USD",
            funding_amount=amount,
            minimum_amount=min_amt,
            maximum_amount=max_amt,
            deadline=exp_date,
            posted_date=start_date,
            status="open" if (exp_date and exp_date >= datetime.utcnow()) else "closed",
            source_url=f"https://www.nsf.gov/awardsearch/showAward?AWD_ID={award_id}",
            last_updated=self._parse_date(raw.get("date") or raw.get("lastUpdate")),
            extra_metadata={
                "directorate": directorate,
                "division": raw.get("div") or raw.get("division"),
                "pi": pi,
                "program_officer": raw.get("poName") or raw.get("programOfficer"),
                "co_pi": raw.get("coPDPI") or raw.get("coPiName"),
            },
        )

    @staticmethod
    def _parse_date(value: Any) -> Optional[datetime]:
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        s = str(value).strip()
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S.%fZ"):
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
