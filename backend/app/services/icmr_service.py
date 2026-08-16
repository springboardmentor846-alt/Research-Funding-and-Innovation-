"""Live ICMR funding scraper. No database storage."""
from app.services.anrf_service import (
    _build_opportunity, _context_after_link, _dedupe, _fetch_html,
    _filter_query, _links, _looks_like_opportunity,
)

ICMR_URL = "https://www.icmr.gov.in/call-for-proposals"


def search_icmr(query: str | None = None, limit: int = 10):
    html = _fetch_html(ICMR_URL)
    items = []
    for title, url in _links(html, ICMR_URL):
        lower = title.lower()
        if not _looks_like_opportunity(title):
            continue
        if not any(x in lower for x in ("call", "proposal", "grant", "eoi", "expression of interest", "research")):
            continue
        context = _context_after_link(html, title)
        item = _build_opportunity(
            source_slug="icmr",
            source_name="ICMR",
            title=title,
            organization="Indian Council of Medical Research",
            official_link=url,
            context=context,
            research_domain="Medical, Biomedical, Clinical and Public Health Research",
            funding_type="Research Grant / Call for Proposal / EOI",
        )
        if item.status == "Open":
            items.append(item)
    return _filter_query(_dedupe(items), query)[:limit]


def get_icmr_opportunity(funding_id: str):
    for item in search_icmr(limit=100):
        if item.id == funding_id:
            return item
    raise ValueError("ICMR opportunity not found or no longer listed.")
