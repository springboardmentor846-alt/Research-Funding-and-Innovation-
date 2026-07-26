from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.publication import Publication
from collections import Counter
from typing import List


def get_all_publications(db: Session, skip: int = 0, limit: int = 20):
    """Fetch paginated publications."""
    total = db.query(Publication).count()
    data = db.query(Publication).offset(skip).limit(limit).all()
    return {"total": total, "data": data}


def get_publication_trends(db: Session):
    """Return publication count grouped by year."""
    results = (
        db.query(Publication.year, func.count(Publication.id).label("count"))
        .group_by(Publication.year)
        .order_by(Publication.year)
        .all()
    )
    return [{"year": r.year, "count": r.count} for r in results]


def get_domain_analysis(db: Session):
    """Return publication count and avg citations per research domain."""
    results = (
        db.query(
            Publication.research_domain,
            func.count(Publication.id).label("count"),
            func.avg(Publication.citation_count).label("avg_citations"),
        )
        .group_by(Publication.research_domain)
        .order_by(func.count(Publication.id).desc())
        .all()
    )
    return [
        {
            "domain": r.research_domain,
            "count": r.count,
            "avg_citations": round(r.avg_citations or 0, 1),
        }
        for r in results
    ]


def get_year_analysis(db: Session):
    """Return detailed year-wise stats including top keywords."""
    pubs = db.query(Publication).all()

    year_map: dict = {}
    for p in pubs:
        yr = p.year
        if yr not in year_map:
            year_map[yr] = {"year": yr, "count": 0, "total_citations": 0, "keywords": []}
        year_map[yr]["count"] += 1
        year_map[yr]["total_citations"] += p.citation_count or 0
        for kw in (p.keywords or "").split(","):
            kw = kw.strip()
            if kw:
                year_map[yr]["keywords"].append(kw)

    result = []
    for yr, data in sorted(year_map.items()):
        top_kw = [k for k, _ in Counter(data["keywords"]).most_common(5)]
        result.append(
            {
                "year": yr,
                "count": data["count"],
                "total_citations": data["total_citations"],
                "top_keywords": top_kw,
            }
        )
    return result


def get_top_keywords(db: Session, limit: int = 20) -> List[dict]:
    """Return the most frequent keywords across all publications."""
    pubs = db.query(Publication.keywords).all()
    all_keywords: List[str] = []
    for (kws,) in pubs:
        for kw in (kws or "").split(","):
            kw = kw.strip()
            if kw:
                all_keywords.append(kw.lower())
    counter = Counter(all_keywords)
    return [{"keyword": k, "count": v} for k, v in counter.most_common(limit)]
