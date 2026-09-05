import re
from collections import defaultdict

import requests as http_requests
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.publication import Publication
from app.schemas.publication import PublicationCreate


def create_publication(db: Session, profile_id: int, data: PublicationCreate, source_type: str = "own"):
    new_pub = Publication(
        profile_id=profile_id,
        title=data.title,
        authors=data.authors,
        year=data.year,
        source=data.source,
        link=data.link,
        source_type=source_type,
    )
    db.add(new_pub)
    db.commit()
    db.refresh(new_pub)
    return new_pub


def get_publications_by_profile(db: Session, profile_id: int):
    """All 'own' publications authored by the researcher (My Publications)."""
    return (
        db.query(Publication)
        .filter(Publication.profile_id == profile_id, Publication.source_type == "own")
        .all()
    )


def get_research_library(db: Session, profile_id: int):
    """External publications imported from OpenAlex for reference (Research Library)."""
    return (
        db.query(Publication)
        .filter(Publication.profile_id == profile_id, Publication.source_type == "external")
        .all()
    )


def get_publication_by_id_for_profile(db: Session, publication_id: int, profile_id: int):
    return (
        db.query(Publication)
        .filter(Publication.id == publication_id, Publication.profile_id == profile_id)
        .first()
    )


def set_publication_pdf_path(db: Session, publication: Publication, pdf_path: str):
    publication.pdf_path = pdf_path
    db.commit()
    db.refresh(publication)
    return publication


def get_publication_trend(db: Session):
    """
    Groups all publications by year and returns a count per year.
    Example: [{"year": "2024", "count": 3}, {"year": "2025", "count": 5}]
    """
    results = (
        db.query(Publication.year, func.count(Publication.id))
        .group_by(Publication.year)
        .order_by(Publication.year)
        .all()
    )

    return [{"year": year if year else "Unknown", "count": count} for year, count in results]


STOPWORDS = {
    "the", "and", "for", "with", "using", "based", "from", "into", "study",
    "analysis", "review", "approach", "towards", "via", "of", "on", "in",
    "to", "a", "an", "is", "are", "new", "novel", "improved", "toward",
    "system", "systems", "model", "models", "method", "methods", "framework"
}


def _extract_words(title: str):
    words = re.findall(r"[a-zA-Z]+", title.lower())
    return [w for w in words if len(w) > 2 and w not in STOPWORDS]


def get_emerging_topics(db: Session, top_n: int = 8):
    """
    Mines keywords from publication titles and compares their frequency
    in the most recent year against all prior years to surface emerging
    research topics.
    """
    publications = db.query(Publication.title, Publication.year).all()

    if not publications:
        return []

    word_year_counts = defaultdict(lambda: defaultdict(int))
    years_seen = set()

    for title, year in publications:
        if not title:
            continue
        year_key = year if year else "Unknown"
        years_seen.add(year_key)
        for word in _extract_words(title):
            word_year_counts[word][year_key] += 1

    numeric_years = [y for y in years_seen if str(y).isdigit()]
    if not numeric_years:
        return []

    latest_year = max(numeric_years, key=lambda y: int(y))

    scored_topics = []
    for word, year_counts in word_year_counts.items():
        recent_count = year_counts.get(latest_year, 0)
        prior_count = sum(c for y, c in year_counts.items() if y != latest_year)

        if recent_count == 0:
            continue

        score = recent_count - prior_count
        scored_topics.append({
            "topic": word,
            "recent_mentions": recent_count,
            "prior_mentions": prior_count,
            "status": "new" if prior_count == 0 else ("growing" if score > 0 else "steady"),
        })

    scored_topics.sort(key=lambda t: (t["recent_mentions"], t["status"] == "new"), reverse=True)
    return scored_topics[:top_n]


def get_research_hotspots(db: Session, top_n: int = 8):
    """
    Identifies the most frequently occurring research keywords across
    all publications (regardless of year) — representing the most
    active/popular research areas (hotspots).
    """
    publications = db.query(Publication.title).all()

    if not publications:
        return []

    word_counts = defaultdict(int)

    for (title,) in publications:
        if not title:
            continue
        for word in _extract_words(title):
            word_counts[word] += 1

    hotspots = [
        {"topic": word, "mentions": count}
        for word, count in word_counts.items()
    ]

    hotspots.sort(key=lambda h: h["mentions"], reverse=True)
    return hotspots[:top_n]


def search_openalex(query: str, limit: int = 10):
    """
    Live search against the OpenAlex API for real research publications
    matching the given query.
    """
    try:
        response = http_requests.get(
            "https://api.openalex.org/works",
            params={"search": query, "per-page": limit, "sort": "publication_date:desc"},
            timeout=10,
        )
        response.raise_for_status()
        works = response.json().get("results", [])
    except Exception:
        return []

    results = []
    for work in works:
        title = work.get("title")
        year = str(work.get("publication_year", ""))
        venue = work.get("host_venue", {}).get("display_name") or "Unknown Source"
        authorships = work.get("authorships", [])
        first_author = authorships[0]["author"]["display_name"] if authorships else "Unknown"

        if not title:
            continue

        results.append({
            "title": title,
            "authors": first_author,
            "year": year,
            "source": venue,
            "link": work.get("id", ""),
        })

    return results