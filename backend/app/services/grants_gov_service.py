"""
Live funding provider integration.

This service intentionally does NOT write funding opportunities to the database.
It fetches current opportunities directly from Grants.gov and normalizes them
into the shape expected by the existing Funding page.
"""

from dataclasses import dataclass, asdict
from datetime import date, datetime
from html import unescape
import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


GRANTS_GOV_API = "https://api.grants.gov/v1/api"
GRANTS_GOV_SITE = "https://www.grants.gov/search-results-detail"

SEARCH_LIMIT = 10
DETAIL_TIMEOUT_SECONDS = 12


@dataclass
class LiveFundingOpportunity:
    id: str
    external_id: str
    source: str
    title: str
    organization: str
    funding_type: str | None = None
    research_domain: str | None = None
    description: str | None = None
    funding_amount: str | None = None
    deadline: date | None = None
    official_link: str | None = None
    country: str | None = None
    eligible_countries: str | None = None
    international_applicants_allowed: bool = False
    career_stage: str | None = None
    qualification: str | None = None
    experience_required: int | None = None
    keywords: str | None = None
    status: str = "Open"
    source_opportunity_number: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _clean_text(value: Any) -> str:
    if value is None:
        return ""

    text = unescape(str(value))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _parse_date(value: Any) -> date | None:
    if not value:
        return None

    value = str(value).strip()

    formats = (
        "%m/%d/%Y",
        "%m/%d/%Y %I:%M:%S %p %Z",
        "%b %d, %Y %I:%M:%S %p EDT",
        "%b %d, %Y %I:%M:%S %p EST",
    )

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass

    # Handle ISO-like strings returned by some API versions.
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def _post_json(endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")

    request = Request(
        endpoint,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "InnovFund/1.0",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=DETAIL_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(
            f"Grants.gov API returned HTTP {exc.code}."
        ) from exc
    except URLError as exc:
        raise RuntimeError(
            "Could not connect to Grants.gov."
        ) from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Grants.gov returned an invalid response."
        ) from exc


def _extract_data(response: dict[str, Any]) -> dict[str, Any]:
    if response.get("errorcode", 0) not in (0, None):
        raise RuntimeError(
            response.get("msg") or "Grants.gov API request failed."
        )

    return response.get("data") or {}


def build_profile_search_keyword(
    domains,
    keywords,
    technologies,
) -> str:
    """
    Build a compact Grants.gov keyword query from the researcher's profile.

    Grants.gov supports keyword search and OR is the default conjunction.
    We therefore send a small set of high-value profile terms rather than
    every field in the profile.
    """
    values: list[str] = []

    for collection in (domains, keywords, technologies):
        for item in collection:
            name = _clean_text(getattr(item, "name", None))
            if name and name.lower() not in {v.lower() for v in values}:
                values.append(name)

    # Keep the external query small and predictable.
    values = values[:6]

    return " ".join(values)


def _parse_search_result(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "external_id": str(item.get("id") or ""),
        "opportunity_number": _clean_text(item.get("number")),
        "title": _clean_text(item.get("title")) or "Untitled Opportunity",
        "organization": (
            _clean_text(item.get("agencyName"))
            or _clean_text(item.get("agencyCode"))
            or "Grants.gov"
        ),
        "open_date": _parse_date(item.get("openDate")),
        "deadline": _parse_date(item.get("closeDate")),
        "status": _clean_text(item.get("oppStatus")) or "posted",
        "aln": ", ".join(
            str(value)
            for value in (item.get("alnist") or [])
            if value
        ),
    }


def _fetch_detail(external_id: str) -> dict[str, Any]:
    response = _post_json(
        f"{GRANTS_GOV_API}/fetchOpportunity",
        {"opportunityId": int(external_id)},
    )
    return _extract_data(response)


def _normalize_detail(
    summary: dict[str, Any],
    detail: dict[str, Any] | None,
) -> LiveFundingOpportunity:
    detail = detail or {}
    synopsis = detail.get("synopsis") or {}

    agency_details = detail.get("agencyDetails") or {}
    organization = (
        _clean_text(synopsis.get("agencyName"))
        or _clean_text(agency_details.get("agencyName"))
        or summary["organization"]
    )

    description = _clean_text(synopsis.get("synopsisDesc"))

    applicant_types = [
        _clean_text(item.get("description"))
        for item in (synopsis.get("applicantTypes") or [])
        if isinstance(item, dict)
    ]
    applicant_types = [item for item in applicant_types if item]

    funding_instruments = [
        _clean_text(item.get("description"))
        for item in (synopsis.get("fundingInstruments") or [])
        if isinstance(item, dict)
    ]
    funding_instruments = [item for item in funding_instruments if item]

    funding_categories = [
        _clean_text(item.get("description"))
        for item in (synopsis.get("fundingActivityCategories") or [])
        if isinstance(item, dict)
    ]
    funding_categories = [item for item in funding_categories if item]

    keywords = " ".join(
        part
        for part in (
            summary.get("title"),
            organization,
            summary.get("aln"),
            " ".join(funding_categories),
        )
        if part
    )

    award_ceiling = (
        _clean_text(synopsis.get("awardCeilingFormatted"))
        or _clean_text(synopsis.get("awardCeiling"))
    )
    award_floor = (
        _clean_text(synopsis.get("awardFloorFormatted"))
        or _clean_text(synopsis.get("awardFloor"))
    )

    if award_ceiling and award_floor:
        funding_amount = f"{award_floor} - {award_ceiling}"
    else:
        funding_amount = award_ceiling or award_floor or None

    deadline = (
        summary.get("deadline")
        or _parse_date(synopsis.get("originalDueDateDesc"))
    )

    funding_type = (
        ", ".join(funding_instruments)
        if funding_instruments
        else None
    )

    # Grants.gov is a US funding source. This field is descriptive only;
    # the detailed eligibility text is shown separately and is not treated
    # as proof of country eligibility.
    eligible_text = ", ".join(applicant_types) or None

    if eligible_text:
        if description:
            description = (
                f"{description}\n\n"
                f"Eligible applicants listed by Grants.gov: "
                f"{eligible_text}."
            )
        else:
            description = (
                "Eligible applicants listed by Grants.gov: "
                f"{eligible_text}."
            )

    return LiveFundingOpportunity(
        id=f"grantsgov-{summary['external_id']}",
        external_id=summary["external_id"],
        source="Grants.gov",
        title=summary["title"],
        organization=organization,
        funding_type=funding_type,
        research_domain=", ".join(funding_categories) or None,
        description=description or None,
        funding_amount=funding_amount,
        deadline=deadline,
        official_link=(
            f"{GRANTS_GOV_SITE}/{summary['external_id']}"
        ),
        country="United States",
        # Grants.gov returns applicant types, not a universal country
        # eligibility field. Keep this separate from country eligibility.
        eligible_countries=None,
        international_applicants_allowed=False,
        keywords=keywords or None,
        status="Open" if summary["status"].lower() == "posted" else summary["status"],
        source_opportunity_number=(
            summary.get("opportunity_number") or None
        ),
    )


def search_grants_gov(
    keyword: str | None = None,
    limit: int = SEARCH_LIMIT,
) -> list[LiveFundingOpportunity]:
    """
    Fetch current posted Grants.gov opportunities.

    No database writes occur here.
    """
    payload = {
        "rows": max(1, min(limit, 25)),
        "keyword": keyword or "",
        "oppStatuses": "posted",
        "eligibilities": "",
        "agencies": "",
        "aln": "",
        "fundingCategories": "",
    }

    response = _post_json(
        f"{GRANTS_GOV_API}/search2",
        payload,
    )
    data = _extract_data(response)

    summaries = data.get("oppHits") or []

    opportunities: list[LiveFundingOpportunity] = []

    for raw_item in summaries[:limit]:
        summary = _parse_search_result(raw_item)

        if not summary["external_id"]:
            continue

        try:
            detail = _fetch_detail(summary["external_id"])
        except RuntimeError:
            # Keep the search useful even if one detail request fails.
            detail = {}

        opportunities.append(
            _normalize_detail(summary, detail)
        )

    return opportunities


def get_grants_gov_opportunity(
    external_id: str,
) -> LiveFundingOpportunity:
    if not str(external_id).isdigit():
        raise ValueError("Invalid Grants.gov opportunity ID.")

    detail = _fetch_detail(str(external_id))

    synopsis = detail.get("synopsis") or {}

    summary = {
        "external_id": str(external_id),
        "opportunity_number": (
            _clean_text(detail.get("opportunityNumber"))
            or _clean_text(detail.get("opportunityTitle"))
        ),
        "title": (
            _clean_text(detail.get("opportunityTitle"))
            or "Untitled Opportunity"
        ),
        "organization": (
            _clean_text(synopsis.get("agencyName"))
            or _clean_text(
                (detail.get("agencyDetails") or {}).get("agencyName")
            )
            or "Grants.gov"
        ),
        "open_date": _parse_date(synopsis.get("postingDate")),
        "deadline": (
            _parse_date(synopsis.get("closingDate"))
            or _parse_date(synopsis.get("originalDueDateDesc"))
        ),
        "status": "posted",
        "aln": ", ".join(
            _clean_text(item.get("alnNumber"))
            for item in (detail.get("alns") or [])
            if isinstance(item, dict) and item.get("alnNumber")
        ),
    }

    return _normalize_detail(summary, detail)
