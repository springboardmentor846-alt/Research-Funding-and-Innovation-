"""
Crossref integration.

Uses Crossref's public REST API (api.crossref.org) which requires no API
key. Adding a contact email in the User-Agent is "polite pool" etiquette
recommended by Crossref for better reliability, but is not required.
Docs: https://api.crossref.org/swagger-ui/index.html
"""
import requests
from app.core.cache import ttl_cache

BASE_URL = "https://api.crossref.org/works"
HEADERS = {"User-Agent": "ResearchFundingPlatform/1.0 (mailto:contact@example.com)"}


def _extract_year(item: dict):
    for date_field in ("published-print", "published-online", "published", "issued"):
        block = item.get(date_field)
        if block and block.get("date-parts"):
            parts = block["date-parts"][0]
            if parts and parts[0]:
                return str(parts[0])
    return None


def _extract_authors(item: dict, limit: int = 3):
    names = []
    for author in item.get("author", []) or []:
        given = author.get("given", "")
        family = author.get("family", "")
        full = f"{given} {family}".strip()
        if full:
            names.append(full)
        if len(names) >= limit:
            break
    return ", ".join(names) if names else None


@ttl_cache(seconds=300)
def search_crossref(query: str, limit: int = 10):
    """
    Live search against Crossref for publication metadata (title, authors,
    year, journal/container, DOI link) matching the given query.
    """
    try:
        response = requests.get(
            BASE_URL,
            params={"query": query, "rows": limit},
            headers=HEADERS,
            timeout=15,
        )
        response.raise_for_status()
        items = response.json().get("message", {}).get("items", [])
    except requests.RequestException:
        return []

    results = []
    for item in items:
        title_list = item.get("title") or []
        title = title_list[0] if title_list else None
        if not title:
            continue

        container_list = item.get("container-title") or []
        source = container_list[0] if container_list else "Unknown Source"

        doi = item.get("DOI")
        link = f"https://doi.org/{doi}" if doi else item.get("URL")

        results.append({
            "title": title[:500],
            "authors": _extract_authors(item),
            "year": _extract_year(item),
            "source": source[:255] if source else None,
            "link": link,
        })

    return results