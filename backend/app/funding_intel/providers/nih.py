"""NIH RePORTER provider.

Endpoint:
    POST https://api.reporter.nih.gov/v2/projects/search

The NIH API is paginated via ``limit`` + ``offset``; there is no
opaque cursor. We synthesise a cursor of the form
``"<offset>:<last_project_num>"`` so the sync engine can resume.

Authentication: none (the API is public and rate-limited upstream).
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
class NIHProvider(BaseProvider):
    """Adapter for the NIH RePORTER v2 ``projects/search`` API."""

    name = "nih"

    def __init__(self) -> None:
        super().__init__(name=self.name)
        s = funding_intel_settings
        self._client: Optional[ProviderHTTPClient] = None
        self._base_url = s.NIH_BASE_URL
        self._page_size = min(s.SYNC_PAGE_SIZE, 500)  # NIH caps at 500

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
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

        # Cursor format: "<offset>:<last_project_num>"
        offset = 0
        if cursor:
            try:
                offset = int(cursor.split(":", 1)[0] or 0)
            except (ValueError, AttributeError):
                offset = 0

        limit = page_size or self._page_size

        payload: Dict[str, Any] = {
            "criteria": {},
            "limit": limit,
            "offset": offset,
            "sort_field": "project_start_date",
            "sort_order": "desc",
        }

        started = __import__("time").perf_counter()

        try:
            data = await self._client.post_json(
                "/projects/search",
                json=payload,
            )
        except Exception as exc:
            self._record_failure(str(exc))
            raise ProviderError(f"NIH request failed: {exc}") from exc

        elapsed_ms = (__import__("time").perf_counter() - started) * 1000.0
        self._record_success(elapsed_ms)

        results = data.get("results") or []
        meta = data.get("meta") or {}

        total = meta.get("total", 0)
        next_offset = offset + len(results)

        # Stop pagination when all records have been fetched
        if not results or next_offset >= total:
            next_cursor = None
        else:
            next_cursor = f"{next_offset}:{results[-1].get('project_num', '')}"

        logger.info(
            f"[NIH] offset={offset}, fetched={len(results)}, "
            f"total={total}, next_cursor={next_cursor}"
        )

        return ProviderBatch(
            records=results,
            next_cursor=next_cursor,
            total_estimated=total,
        )

    # ------------------------------------------------------------------
    # Normalize
    # ------------------------------------------------------------------
    def normalize(self, raw: Dict[str, Any]) -> Optional[NormalizedFunding]:
        if not isinstance(raw, dict):
            return None

        project_num = raw.get("project_num") or raw.get("application_id")
        if not project_num:
            return None

        title = (raw.get("project_title") or raw.get("title") or "").strip()
        abstract = (raw.get("abstract_text") or raw.get("description") or "").strip()
        if not title:
            return None

        org_name = None
        org = raw.get("organization") or {}
        if isinstance(org, dict):
            org_name = org.get("name") or org.get("org_name")

        # Funding
        award_amount = raw.get("award_amount")
        if isinstance(award_amount, str):
            try:
                award_amount = float(award_amount)
            except (TypeError, ValueError):
                award_amount = None

        # Dates
        deadline = self._parse_date(raw.get("project_end_date"))
        posted = self._parse_date(raw.get("project_start_date"))
        last_updated = self._parse_date(raw.get("last_update_date"))

        # Agency / org
        agency = None
        org_full = raw.get("organization") or {}
        if isinstance(org_full, dict):
            agency = org_full.get("department") or org_full.get("agency")

        # Keywords
        terms = raw.get("terms") or ""
        if isinstance(terms, list):
            keywords = ", ".join(str(t) for t in terms if t)
        else:
            keywords = str(terms) if terms else None

        return NormalizedFunding(
            source=self.name,
            source_id=str(project_num),
            title=title[:500],
            description=(abstract or title)[:8000],
            agency=agency,
            organization=org_name,
            country="United States",
            research_area=org_name,
            funding_type="grant",
            keywords=keywords,
            eligibility=raw.get("awardee_name"),
            funding_amount=award_amount,
            currency="USD",
            minimum_amount=award_amount,
            maximum_amount=award_amount,
            deadline=deadline,
            posted_date=posted,
            status="open" if (deadline and deadline >= datetime.utcnow()) else "closed",
            source_url=f"https://reporter.nih.gov/project-details/{project_num}",
            last_updated=last_updated,
            extra_metadata={
                "fiscal_year": raw.get("fiscal_year"),
                "award_type": raw.get("award_type"),
                "activity_code": raw.get("activity_code"),
                "pi_names": raw.get("pi_names"),
                "org_city": (raw.get("organization") or {}).get("city") if isinstance(raw.get("organization"), dict) else None,
                "org_state": (raw.get("organization") or {}).get("state") if isinstance(raw.get("organization"), dict) else None,
            },
        )

    @staticmethod
    def _parse_date(value: Any) -> Optional[datetime]:
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        try:
            # NIH returns ISO strings
            return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
        except (TypeError, ValueError):
            return None
