"""Live EU Funding & Tenders / Horizon Europe provider.

Uses the European Commission's public REST search API.
No opportunities are stored in PostgreSQL.
"""
from __future__ import annotations

from datetime import date, datetime
from html import unescape
from hashlib import sha1
import base64
import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from app.services.grants_gov_service import LiveFundingOpportunity

EU_SEARCH_API = (
    "https://api.tech.ec.europa.eu/search-api/prod/rest/search"
    "?apiKey=SEDIA"
)
EU_PORTAL = "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-search"

def _clean(v):
    if v is None:
        return ""
    return re.sub(r"\s+", " ", unescape(str(v))).strip()

def _parse_date(v):
    if not v:
        return None
    s = _clean(v)
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s[:10], fmt).date()
        except ValueError:
            pass
    m = re.search(r"(\d{4}-\d{2}-\d{2})", s)
    if m:
        try:
            return date.fromisoformat(m.group(1))
        except ValueError:
            pass
    return None

def _post(text, query, page_size=20):
    payload = json.dumps(query).encode("utf-8")
    url = f"{EU_SEARCH_API}&text={quote(text or '')}&pageSize={page_size}"
    req = Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "InnovFund/1.0",
        },
    )
    try:
        with urlopen(req, timeout=18) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"EU Funding & Tenders API returned HTTP {exc.code}.") from exc
    except URLError as exc:
        raise RuntimeError("Could not connect to the EU Funding & Tenders API.") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("EU Funding & Tenders returned an invalid response.") from exc

def _objects(value):
    if isinstance(value, dict):
        yield value
        for v in value.values():
            yield from _objects(v)
    elif isinstance(value, list):
        for v in value:
            yield from _objects(v)

def _first(obj, names):
    for name in names:
        if name in obj and obj[name] not in (None, ""):
            return obj[name]
    return None

def _make(item):
    identifier = _clean(_first(item, (
        "identifier", "identifierCode", "callIdentifier", "topicIdentifier",
        "topicId", "id", "reference",
    )))
    title = _clean(_first(item, ("title", "title_en", "topicTitle", "name")))
    if not identifier or not title:
        return None

    deadline = _parse_date(_first(item, (
        "deadlineDate", "deadline", "submissionDeadline", "closeDate",
    )))
    opening = _parse_date(_first(item, (
        "openingDate", "startDate", "openDate",
    )))
    description = _clean(_first(item, (
        "description", "description_en", "summary", "topicDescription",
    )))
    url = _clean(_first(item, ("url", "topicUrl", "link")))
    if not url:
        url = f"{EU_PORTAL}?query={quote(identifier)}"

    status = _clean(_first(item, ("status", "statusLabel"))) or "Open"
    if deadline and deadline < date.today():
        status = "Closed"

    encoded = base64.urlsafe_b64encode(identifier.encode("utf-8")).decode("ascii").rstrip("=")
    return LiveFundingOpportunity(
        id=f"eufunding-v2-{encoded}",
        external_id=identifier,
        source="Horizon Europe / EU Funding & Tenders",
        title=title,
        organization="European Commission",
        funding_type="EU Grant / Call for Proposal",
        research_domain="European Research and Innovation",
        description=description[:1800] or None,
        funding_amount=None,
        deadline=deadline,
        official_link=url,
        country="European Union",
        eligible_countries="See call-specific eligibility",
        international_applicants_allowed=True,
        career_stage=None,
        qualification=None,
        experience_required=None,
        keywords=f"{title} {identifier} {description[:600]}",
        status=status,
        source_opportunity_number=identifier,
    )

def search_horizon(query: str | None = None, limit: int = 8):
    # Public API examples use type 1/2/8 for grants/topics and status codes
    # 31094501/31094502 for open/ongoing states.
    filter_query = {
        "bool": {
            "must": [
                {"terms": {"type": ["1", "2", "8"]}},
                {"terms": {"status": ["31094501", "31094502"]}},
            ]
        }
    }
    response = _post(query or "", filter_query, page_size=max(20, limit * 3))
    results = []
    seen = set()
    for obj in _objects(response):
        item = _make(obj)
        if not item or item.id in seen:
            continue
        if item.status.lower() == "closed":
            continue
        seen.add(item.id)
        results.append(item)
        if len(results) >= limit:
            break
    return results

def get_horizon_opportunity(funding_id: str):
    if funding_id.startswith("eufunding-v2-"):
        encoded = funding_id.removeprefix("eufunding-v2-")
        padding = "=" * (-len(encoded) % 4)
        try:
            identifier = base64.urlsafe_b64decode(
                encoded + padding
            ).decode("utf-8")
        except Exception as exc:
            raise ValueError("Invalid EU/Horizon opportunity ID.") from exc

        # Query the EU API directly using the stable topic/call identifier.
        for item in search_horizon(query=identifier, limit=50):
            if item.external_id == identifier:
                return item

        raise ValueError(
            "EU/Horizon opportunity is no longer available from the live source."
        )

    # Backward compatibility for cards generated before this fix.
    legacy_hash = funding_id.removeprefix("eufunding-")
    for item in search_horizon(limit=100):
        digest = sha1(item.external_id.encode("utf-8")).hexdigest()[:16]
        if digest == legacy_hash:
            return item

    raise ValueError("EU/Horizon opportunity not found or no longer listed.")
