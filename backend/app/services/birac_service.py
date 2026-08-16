"""Live BIRAC funding scraper. No database storage."""
from app.services.anrf_service import (
    _build_opportunity, _context_after_link, _dedupe, _fetch_html,
    _filter_query, _links, _looks_like_opportunity,
)

BIRAC_URL = "https://www.birac.nic.in/cfp.php"


def search_birac(query: str | None = None, limit: int = 10):
    html = _fetch_html(BIRAC_URL)
    items = []
    for title, url in _links(html, BIRAC_URL):
        lower = title.lower()
        if not _looks_like_opportunity(title):
            continue
        if not any(x in lower for x in ("call", "proposal", "grant", "fund", "challenge", "innovation")):
            continue
        context = _context_after_link(html, title)
        item = _build_opportunity(
            source_slug="birac",
            source_name="BIRAC",
            title=title,
            organization="Biotechnology Industry Research Assistance Council",
            official_link=url,
            context=context,
            research_domain="Biotechnology, Healthcare, Biomanufacturing, Startups and Innovation",
            funding_type="Call for Proposal / Innovation Funding",
        )
        if item.status == "Open":
            items.append(item)
    return _filter_query(_dedupe(items), query)[:limit]


def get_birac_opportunity(funding_id: str):
    for item in search_birac(limit=100):
        if item.id == funding_id:
            return item
    raise ValueError("BIRAC opportunity not found or no longer listed.")
