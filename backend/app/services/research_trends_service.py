"""
Research Trends service.

Aggregates existing platform data (publications, research profile domains /
keywords / technology areas) into chart-ready summaries: publications per
year, and the most common domains / keywords / technology areas across all
researchers. No new tables — reuses Publication, ResearchDomain,
ResearchKeyword and TechnologyArea.
"""
from collections import Counter

from sqlalchemy.orm import Session

from app.models.publication import Publication
from app.models.profile_entities import ResearchDomain, ResearchKeyword, TechnologyArea


def publications_by_year(db: Session) -> list[dict]:
    """Count of publications per year, sorted chronologically.

    Skips rows with a missing/non-numeric year rather than failing, since
    `year` is a free-text field that isn't guaranteed to be clean.
    """
    counts: Counter = Counter()
    for (year,) in db.query(Publication.year).all():
        if year and str(year).strip().isdigit():
            counts[str(year).strip()] += 1

    return [{"year": year, "count": count} for year, count in sorted(counts.items())]


def _top_names(db: Session, model, limit: int) -> list[dict]:
    counts: Counter = Counter()
    for (name,) in db.query(model.name).all():
        if name and name.strip():
            counts[name.strip()] += 1

    return [{"name": name, "count": count} for name, count in counts.most_common(limit)]


def top_domains(db: Session, limit: int = 10) -> list[dict]:
    return _top_names(db, ResearchDomain, limit)


def top_keywords(db: Session, limit: int = 20) -> list[dict]:
    """Word-cloud-ready keyword frequency list."""
    return _top_names(db, ResearchKeyword, limit)


def top_technology_areas(db: Session, limit: int = 10) -> list[dict]:
    return _top_names(db, TechnologyArea, limit)


def trends_overview(db: Session) -> dict:
    return {
        "publications_by_year": publications_by_year(db),
        "top_domains": top_domains(db),
        "top_keywords": top_keywords(db),
        "top_technology_areas": top_technology_areas(db),
    }