"""Live UKRI Funding Finder provider.

UKRI publishes a public funding finder. This provider reads the current
opportunity listing page and normalizes matching links; it does not store data.
"""
from __future__ import annotations

from datetime import date, datetime
from hashlib import sha1
import base64
from html import unescape
from html.parser import HTMLParser
import re
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from app.services.grants_gov_service import LiveFundingOpportunity

UKRI_URL = "https://www.ukri.org/opportunity/?keywords=apply+for+funding"

class _Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href = None
        self.text = []
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self.href = dict(attrs).get("href")
            self.text = []
    def handle_data(self, data):
        if self.href is not None:
            self.text.append(data)
    def handle_endtag(self, tag):
        if tag.lower() == "a" and self.href:
            text = re.sub(r"\s+", " ", unescape(" ".join(self.text))).strip()
            if text:
                self.links.append((text, urljoin(UKRI_URL, self.href)))
            self.href = None
            self.text = []

def _fetch():
    req = Request(
        UKRI_URL,
        headers={"User-Agent": "Mozilla/5.0 InnovFund/1.0", "Accept": "text/html"},
    )
    try:
        with urlopen(req, timeout=18) as r:
            return r.read().decode("utf-8", errors="ignore")
    except HTTPError as exc:
        raise RuntimeError(f"UKRI Funding Finder returned HTTP {exc.code}.") from exc
    except URLError as exc:
        raise RuntimeError("Could not connect to UKRI Funding Finder.") from exc

def _parse_date(s):
    if not s:
        return None
    m = re.search(r"(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})", s, re.I)
    if m:
        try:
            return datetime.strptime(m.group(1), "%d %B %Y").date()
        except ValueError:
            pass
    return None

def _context(html, title):
    pos = html.lower().find(title.lower())
    if pos < 0:
        return title
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html[pos:pos+1400]))).strip()

def search_ukri(query: str | None = None, limit: int = 8):
    html = _fetch()
    parser = _Parser()
    parser.feed(html)
    words = [w.lower() for w in re.findall(r"[A-Za-z0-9+#.-]+", query or "") if len(w) > 1]
    candidates = []
    seen = set()

    for title, url in parser.links:
        low = title.lower()
        if len(title) < 12 or url in seen:
            continue
        if not any(x in low for x in ("fund", "grant", "fellowship", "award", "research", "call", "funding")):
            continue
        if any(x in low for x in ("cookie", "privacy", "contact", "sign in", "menu")):
            continue
        context = _context(html, title)
        haystack = f"{title} {context}".lower()
        score = sum(1 for word in words if word in haystack)
        if words and score == 0:
            continue
        seen.add(url)
        encoded_url = base64.urlsafe_b64encode(url.encode("utf-8")).decode("ascii").rstrip("=")
        deadline = _parse_date(context)
        if deadline and deadline < date.today():
            continue
        candidates.append((
            score,
            LiveFundingOpportunity(
                id=f"ukri-v2-{encoded_url}",
                external_id=url,
                source="UKRI",
                title=title,
                organization="UK Research and Innovation",
                funding_type="Grant / Fellowship / Research Call",
                research_domain="Research and Innovation",
                description=context[:1800] or None,
                funding_amount=None,
                deadline=deadline,
                official_link=url,
                country="United Kingdom",
                eligible_countries="See call-specific eligibility",
                international_applicants_allowed=True,
                career_stage=None,
                qualification=None,
                experience_required=None,
                keywords=f"{title} {context[:600]}",
                status="Open",
                source_opportunity_number=None,
            ),
        ))
    candidates.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in candidates[:limit]]

def get_ukri_opportunity(funding_id: str):
    if funding_id.startswith("ukri-v2-"):
        encoded = funding_id.removeprefix("ukri-v2-")
        padding = "=" * (-len(encoded) % 4)
        try:
            url = base64.urlsafe_b64decode(
                encoded + padding
            ).decode("utf-8")
        except Exception as exc:
            raise ValueError("Invalid UKRI opportunity ID.") from exc

        for item in search_ukri(limit=100):
            if item.official_link == url:
                return item

        raise ValueError(
            "UKRI opportunity is no longer available from the live source."
        )

    # Backward compatibility for old hashed IDs.
    legacy_hash = funding_id.removeprefix("ukri-")
    for item in search_ukri(limit=100):
        digest = sha1(item.official_link.encode("utf-8")).hexdigest()[:16]
        if digest == legacy_hash:
            return item

    raise ValueError("UKRI opportunity not found or no longer listed.")
