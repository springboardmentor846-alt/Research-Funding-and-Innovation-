"""Live DBT funding scraper. No database storage."""
from app.services.anrf_service import (
    _build_opportunity, _context_after_link, _dedupe, _fetch_html,
    _filter_query, _links, _looks_like_opportunity,
)

DBT_URL = "https://www.dbtindia.gov.in/latest-announcement"


def search_dbt(query: str | None = None, limit: int = 10):
    html = _fetch_html(DBT_URL)
    items = []
    for title, url in _links(html, DBT_URL):
        lower = title.lower()
        if not _looks_like_opportunity(title):
            continue
        if not any(x in lower for x in ("call", "proposal", "grant", "fellowship", "research")):
            continue
        context = _context_after_link(html, title)
        item = _build_opportunity(
            source_slug="dbt",
            source_name="DBT",
            title=title,
            organization="Department of Biotechnology, Government of India",
            official_link=url,
            context=context,
            research_domain="Biotechnology, Life Sciences, Bioinformatics and Biomanufacturing",
            funding_type="Call for Proposal / Research Grant",
        )
        if item.status == "Open":
            items.append(item)
    return _filter_query(_dedupe(items), query)[:limit]


def get_dbt_opportunity(funding_id: str):
    for item in search_dbt(limit=100):
        if item.id == funding_id:
            return item
    raise ValueError("DBT opportunity not found or no longer listed.")
