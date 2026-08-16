"""
ANRF scraper + shared helpers for Indian funding sources.

No funding opportunities are stored in PostgreSQL.
Only public pages are fetched at request time.
"""
from __future__ import annotations

from datetime import date, datetime
from hashlib import sha1
from html import unescape
from html.parser import HTMLParser
import re
from typing import Iterable
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from app.services.grants_gov_service import LiveFundingOpportunity


ANRF_URL = "https://www.anrf.gov.in/page/english/research_grants"
TIMEOUT_SECONDS = 15

OPPORTUNITY_WORDS = (
    "call", "proposal", "grant", "fellowship", "scheme", "programme",
    "program", "research", "mission", "award", "fund", "support",
)

DATE_PATTERNS = (
    "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",
    "%d %B %Y", "%d %b %Y",
    "%B %d, %Y", "%b %d, %Y",
)


class _LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self._href = None
        self._text = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self._href is not None:
            text = _clean_text(" ".join(self._text))
            if text and self._href:
                self.links.append((text, self._href))
            self._href = None
            self._text = []


def _clean_text(value) -> str:
    if value is None:
        return ""
    text = unescape(str(value))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _fetch_html(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 InnovFund/1.0",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8", errors="ignore")
    except HTTPError as exc:
        raise RuntimeError(f"Indian funding source returned HTTP {exc.code}.") from exc
    except URLError as exc:
        raise RuntimeError("Could not connect to Indian funding source.") from exc


def _links(html: str, base_url: str):
    parser = _LinkParser()
    parser.feed(html)
    seen = set()
    output = []
    for text, href in parser.links:
        url = urljoin(base_url, href)
        key = (text.lower(), url)
        if key not in seen:
            seen.add(key)
            output.append((text, url))
    return output


def _parse_date(text: str) -> date | None:
    if not text:
        return None

    # Prefer explicit dates near "last date", "deadline", "closing", etc.
    candidates = re.findall(
        r"(?:last\s+date|deadline|closing\s+date|end\s+date|submission\s+date)?"
        r"[^0-9A-Za-z]{0,20}"
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{4}|"
        r"\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}|"
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|"
        r"Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4})",
        text,
        flags=re.I,
    )

    parsed = []
    for value in candidates:
        value = re.sub(r"\s+", " ", value.strip()).replace(",", ",")
        for fmt in DATE_PATTERNS:
            try:
                parsed.append(datetime.strptime(value, fmt).date())
                break
            except ValueError:
                pass

    # Usually the latest date in a call listing is the submission deadline.
    return max(parsed) if parsed else None


def _context_after_link(html: str, title: str, chars: int = 900) -> str:
    # Best-effort context extraction. If exact HTML text differs because of
    # entities/markup, falling back to the title still keeps the result usable.
    pos = html.lower().find(title.lower())
    if pos < 0:
        return title
    return _clean_text(html[pos:pos + chars])


def _make_id(source_slug: str, official_link: str) -> str:
    digest = sha1(official_link.encode("utf-8")).hexdigest()[:16]
    return f"{source_slug}-{digest}"


def _looks_like_opportunity(title: str) -> bool:
    lower = title.lower()
    if len(title) < 8:
        return False
    blocked = (
        "home", "contact", "login", "register", "faq", "download",
        "privacy", "terms", "sitemap", "annual report", "vacancy",
        "tender", "news", "read more",
    )
    if any(x == lower or lower.startswith(x + " ") for x in blocked):
        return False
    return any(word in lower for word in OPPORTUNITY_WORDS)


def _dedupe(items: Iterable[LiveFundingOpportunity]):
    seen = set()
    result = []
    for item in items:
        key = (item.source.lower(), item.official_link or item.title.lower())
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _filter_query(items, query: str | None):
    if not query:
        return list(items)
    words = {w.lower() for w in re.findall(r"[A-Za-z0-9+#.-]+", query) if len(w) > 1}
    if not words:
        return list(items)

    scored = []
    for item in items:
        haystack = " ".join([
            item.title or "", item.organization or "", item.description or "",
            item.research_domain or "", item.keywords or "",
        ]).lower()
        score = sum(1 for word in words if word in haystack)
        if score:
            scored.append((score, item))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored]


def _build_opportunity(
    *,
    source_slug: str,
    source_name: str,
    title: str,
    organization: str,
    official_link: str,
    context: str,
    research_domain: str,
    funding_type: str = "Call for Proposal",
) -> LiveFundingOpportunity:
    deadline = _parse_date(context)
    return LiveFundingOpportunity(
        id=_make_id(source_slug, official_link),
        external_id=_make_id(source_slug, official_link).split("-", 1)[1],
        source=source_name,
        title=_clean_text(title),
        organization=organization,
        funding_type=funding_type,
        research_domain=research_domain,
        description=_clean_text(context)[:1800] or None,
        funding_amount=None,
        deadline=deadline,
        official_link=official_link,
        country="India",
        eligible_countries="India",
        international_applicants_allowed=False,
        career_stage=None,
        qualification=None,
        experience_required=None,
        keywords=f"{title} {research_domain} {organization}",
        status="Open" if deadline is None or deadline >= date.today() else "Closed",
        source_opportunity_number=None,
    )


def search_anrf(query: str | None = None, limit: int = 10):
    html = _fetch_html(ANRF_URL)
    items = []

    for title, url in _links(html, ANRF_URL):
        if not _looks_like_opportunity(title):
            continue
        context = _context_after_link(html, title)
        item = _build_opportunity(
            source_slug="anrf",
            source_name="ANRF",
            title=title,
            organization="Anusandhan National Research Foundation",
            official_link=url,
            context=context,
            research_domain="Science, Technology, Engineering and Interdisciplinary Research",
            funding_type="Research Grant / Call for Proposal",
        )
        if item.status == "Open":
            items.append(item)

    items = _filter_query(_dedupe(items), query)
    return items[:limit]


def get_anrf_opportunity(funding_id: str):
    for item in search_anrf(limit=100):
        if item.id == funding_id:
            return item
    raise ValueError("ANRF opportunity not found or no longer listed.")
