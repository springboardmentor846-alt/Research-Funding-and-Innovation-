import re
from collections import defaultdict

import requests as http_requests
from sqlalchemy.orm import Session
from app.models.patent import Patent
from app.schemas.patent import PatentCreate


def search_patentsview(keyword: str, limit: int = 10):
    """
    Live search against the PatentsView public API (USPTO) for real
    granted patents matching the given keyword in their title.
    """
    try:
        query = {
            "q": {"_text_any": {"patent_title": keyword}},
            "f": ["patent_id", "patent_title", "patent_date", "assignees.assignee_organization"],
            "o": {"size": limit},
        }
        response = http_requests.get(
            "https://search.patentsview.org/api/v1/patent/",
            params={"q": http_requests.utils.quote(str(query))},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        hits = data.get("patents", [])
    except Exception:
        return []

    results = []
    for hit in hits:
        assignees = hit.get("assignees") or []
        assignee_name = assignees[0].get("assignee_organization") if assignees else "Unknown"
        results.append({
            "title": hit.get("patent_title", "Untitled Patent"),
            "assignee": assignee_name or "Unknown",
            "filing_date": hit.get("patent_date", "Not specified"),
            "patent_number": hit.get("patent_id", "N/A"),
        })

    return results


def create_patent(db: Session, profile_id: int, data: PatentCreate):
    new_patent = Patent(
        profile_id=profile_id,
        title=data.title,
        assignee=data.assignee,
        filing_date=data.filing_date,
        patent_number=data.patent_number,
    )
    db.add(new_patent)
    db.commit()
    db.refresh(new_patent)
    return new_patent


def get_patents_by_profile(db: Session, profile_id: int):
    return db.query(Patent).filter(Patent.profile_id == profile_id).all()


def _extract_year(filing_date: str):
    if not filing_date:
        return "Unknown"
    match = re.search(r"(19|20)\d{2}", filing_date)
    return match.group(0) if match else "Unknown"


def get_patent_trend(db: Session):
    """
    Groups all patents by filing year and returns a count per year.
    Example: [{"year": "2024", "count": 2}, {"year": "2025", "count": 3}]
    """
    patents = db.query(Patent.filing_date).all()

    year_counts = defaultdict(int)
    for (filing_date,) in patents:
        year = _extract_year(filing_date)
        year_counts[year] += 1

    results = [{"year": year, "count": count} for year, count in year_counts.items()]
    results.sort(key=lambda r: r["year"])
    return results


def get_competitor_analysis(db: Session, top_n: int = 8):
    """
    Groups patents by assignee to identify the most active
    organizations/competitors in the patent landscape.
    """
    patents = db.query(Patent.assignee).all()

    assignee_counts = defaultdict(int)
    for (assignee,) in patents:
        name = assignee if assignee else "Unknown"
        assignee_counts[name] += 1

    results = [{"assignee": name, "patent_count": count} for name, count in assignee_counts.items()]
    results.sort(key=lambda r: r["patent_count"], reverse=True)
    return results[:top_n]


STOPWORDS = {
    "the", "and", "for", "with", "using", "based", "from", "into", "system",
    "systems", "method", "methods", "device", "devices", "apparatus", "of",
    "on", "in", "to", "a", "an", "is", "are", "new", "improved"
}


def _extract_words(title: str):
    words = re.findall(r"[a-zA-Z]+", title.lower())
    return [w for w in words if len(w) > 2 and w not in STOPWORDS]


def get_technology_clusters(db: Session, top_n: int = 8):
    """
    Extracts keywords from patent titles to map the most common
    technology areas represented in the patent portfolio (innovation mapping).
    """
    patents = db.query(Patent.title).all()

    word_counts = defaultdict(int)
    for (title,) in patents:
        if not title:
            continue
        for word in _extract_words(title):
            word_counts[word] += 1

    clusters = [{"technology": word, "mentions": count} for word, count in word_counts.items()]
    clusters.sort(key=lambda c: c["mentions"], reverse=True)
    return clusters[:top_n]