import asyncio
from datetime import date
import httpx

OPENALEX = "https://api.openalex.org/works"
CONTACT_EMAIL = "innovation-platform@example.com"


async def _get(client: httpx.AsyncClient, params: dict) -> dict:
    params = {**params, "mailto": CONTACT_EMAIL}
    resp = await client.get(OPENALEX, params=params)
    resp.raise_for_status()
    return resp.json()


def _year_window(rows: list[dict], span: int = 12) -> list[dict]:
    current = date.today().year
    cleaned = []
    for r in rows:
        try:
            y = int(r["key"])
        except (ValueError, TypeError):
            continue
        if current - span < y <= current:
            cleaned.append({"year": y, "count": r["count"]})
    return sorted(cleaned, key=lambda x: x["year"])


def _emerging(all_topics: list[dict], recent_topics: list[dict],
              total_all: int, total_recent: int, limit: int = 6) -> list[dict]:
    if not total_all or not total_recent:
        return []
    all_share = {t["key_display_name"]: t["count"] / total_all for t in all_topics}
    out = []
    for t in recent_topics:
        name = t["key_display_name"]
        recent_share = t["count"] / total_recent
        base = all_share.get(name, 0.0)
        growth = recent_share - base
        if growth > 0:
            out.append({
                "topic": name,
                "recent_share": round(recent_share * 100, 1),
                "growth": round(growth * 100, 1),
            })
    out.sort(key=lambda x: x["growth"], reverse=True)
    return out[:limit]


async def get_trends(query: str, topic_limit: int = 10, paper_limit: int = 5) -> dict:
    recent_from = f"{date.today().year - 2}-01-01"
    async with httpx.AsyncClient(timeout=25) as client:
        by_year, all_topics, recent_topics, top_papers = await asyncio.gather(
            _get(client, {"search": query, "group_by": "publication_year"}),
            _get(client, {"search": query, "group_by": "topics.id"}),
            _get(client, {"search": query, "group_by": "topics.id",
                          "filter": f"from_publication_date:{recent_from}"}),
            _get(client, {"search": query, "sort": "cited_by_count:desc",
                          "per-page": paper_limit}),
        )

    total_works = top_papers["meta"]["count"]
    total_recent = recent_topics["meta"]["count"]

    hotspots = [{"topic": t["key_display_name"], "count": t["count"]}
                for t in all_topics["group_by"][:topic_limit]]

    emerging = _emerging(all_topics["group_by"], recent_topics["group_by"],
                         total_works, total_recent)

    papers = []
    for w in top_papers["results"]:
        loc = w.get("primary_location") or {}
        papers.append({
            "title": w.get("title") or "Untitled",
            "year": w.get("publication_year"),
            "cited_by_count": w.get("cited_by_count") or 0,
            "venue": (loc.get("source") or {}).get("display_name"),
            "url": loc.get("landing_page_url") or w.get("doi"),
        })

    return {
        "query": query,
        "total_works": total_works,
        "works_by_year": _year_window(by_year["group_by"]),
        "hotspots": hotspots,
        "emerging_topics": emerging,
        "top_papers": papers,
    }
