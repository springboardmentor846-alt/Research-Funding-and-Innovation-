"""Live Wellcome funding provider.

Wellcome exposes a public Funding Platform API endpoint, but its public API
schema is not documented as a stable consumer contract. For this project we
use Wellcome's public research-funding pages as the source of current scheme
links. No funding data is stored.
"""
from __future__ import annotations

from datetime import date
from hashlib import sha1
import base64
from html import unescape
from html.parser import HTMLParser
import re
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from app.services.grants_gov_service import LiveFundingOpportunity

WELLCOME_URL = "https://wellcome.org/grant-funding"

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
                self.links.append((text, urljoin(WELLCOME_URL, self.href)))
            self.href = None
            self.text = []

def _fetch():
    req = Request(
        WELLCOME_URL,
        headers={"User-Agent": "Mozilla/5.0 InnovFund/1.0", "Accept": "text/html"},
    )
    try:
        with urlopen(req, timeout=18) as r:
            return r.read().decode("utf-8", errors="ignore")
    except HTTPError as exc:
        raise RuntimeError(f"Wellcome funding page returned HTTP {exc.code}.") from exc
    except URLError as exc:
        raise RuntimeError("Could not connect to Wellcome funding pages.") from exc

def search_wellcome(query: str | None = None, limit: int = 8):
    html = _fetch()
    parser = _Parser()
    parser.feed(html)
    words = [w.lower() for w in re.findall(r"[A-Za-z0-9+#.-]+", query or "") if len(w) > 1]
    results = []
    seen = set()

    for title, url in parser.links:
        low = title.lower()
        if url in seen or len(title) < 8:
            continue
        if not any(x in low for x in ("award", "research", "fund", "discovery", "mental health", "infectious", "climate")):
            continue
        if "/grant-funding/" not in url:
            continue
        context = re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html[max(0, html.lower().find(title.lower())):max(0, html.lower().find(title.lower()))+1200]))).strip()
        haystack = f"{title} {context}".lower()
        score = sum(1 for word in words if word in haystack)
        if words and score == 0:
            continue
        seen.add(url)
        encoded_url = base64.urlsafe_b64encode(url.encode("utf-8")).decode("ascii").rstrip("=")
        results.append((
            score,
            LiveFundingOpportunity(
                id=f"wellcome-v2-{encoded_url}",
                external_id=url,
                source="Wellcome",
                title=title,
                organization="Wellcome",
                funding_type="Research Grant / Award",
                research_domain="Life, Health and Wellbeing",
                description=context[:1800] or None,
                funding_amount=None,
                deadline=None,
                official_link=url,
                country="Global",
                eligible_countries="See scheme-specific eligibility",
                international_applicants_allowed=True,
                career_stage="Early, mid-career or established depending on scheme",
                qualification=None,
                experience_required=None,
                keywords=f"{title} {context[:700]}",
                status="Open",
                source_opportunity_number=None,
            ),
        ))
    results.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in results[:limit]]

def get_wellcome_opportunity(funding_id: str):
    if funding_id.startswith("wellcome-v2-"):
        encoded = funding_id.removeprefix("wellcome-v2-")
        padding = "=" * (-len(encoded) % 4)
        try:
            url = base64.urlsafe_b64decode(
                encoded + padding
            ).decode("utf-8")
        except Exception as exc:
            raise ValueError("Invalid Wellcome opportunity ID.") from exc

        for item in search_wellcome(limit=100):
            if item.official_link == url:
                return item

        raise ValueError(
            "Wellcome opportunity is no longer available from the live source."
        )

    # Backward compatibility for old hashed IDs.
    legacy_hash = funding_id.removeprefix("wellcome-")
    for item in search_wellcome(limit=100):
        digest = sha1(item.official_link.encode("utf-8")).hexdigest()[:16]
        if digest == legacy_hash:
            return item

    raise ValueError("Wellcome opportunity not found or no longer listed.")
