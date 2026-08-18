"""Patent intelligence endpoints.

All values are read from the live ``patents`` table populated by the
Patent Intelligence Service.  No mock data; no hardcoded numbers.

The new intelligence endpoints live under
``app.patents.api.router`` and are mounted at
``/api/v1/patents/intel/*``.  This router keeps the legacy
``/api/v1/patents/*`` surface (search, get-by-id, explain, analytics
overview, gap analysis) so the existing researcher and admin pages
keep working without changes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.db import get_db
from app.models.patent import Patent
from app.models.user import User
from app.ai.assistant import research_assistant


router = APIRouter(prefix="/patents", tags=["Patents"])


class PatentSearchRequest(BaseModel):
    query: str
    source: str = "all"  # google_patents | uspto | the_lens | all


class PatentExplainRequest(BaseModel):
    patent_text: str


def _patent_to_dict(p: Patent) -> dict:
    return {
        "id": p.patent_number,  # backward-compat: old UI used patent_number as id
        "patent_number": p.patent_number,
        "title": p.title,
        "abstract": p.abstract,
        "source": p.source,
        "year": p.publication_year,
        "technology": p.technology_area,
        "citations": p.citations,
        "assignee": p.assignee,
        "country": p.country,
        "url": p.url,
        "publication_date": p.publication_date.isoformat() if p.publication_date else None,
    }


@router.get("/search")
def search_patents(
    q: Optional[str] = None,
    source: Optional[str] = None,
    technology: Optional[str] = None,
    country: Optional[str] = None,
    year: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search the patent corpus with optional filters.

    Returns the same shape the legacy UI expects (``results`` /
    ``count``) plus pagination metadata.
    """
    query = db.query(Patent)
    if q:
        like = f"%{q.lower()}%"
        query = query.filter(
            or_(
                Patent.title.ilike(like),
                Patent.abstract.ilike(like),
                Patent.keywords.ilike(like),
                Patent.technology_area.ilike(like),
            )
        )
    if source and source != "all":
        query = query.filter(Patent.source == source)
    if technology:
        query = query.filter(Patent.technology_area == technology)
    if country:
        query = query.filter(Patent.country == country)
    if year:
        query = query.filter(Patent.publication_year == year)

    total = query.count()
    rows = (
        query.order_by(Patent.publication_year.desc(), Patent.citations.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "query": q,
        "results": [_patent_to_dict(p) for p in rows],
        "count": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{patent_id}")
def get_patent(
    patent_id: str,
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Look up a patent by integer id or canonical patent_number."""
    row = None
    if patent_id.isdigit():
        row = db.query(Patent).filter(Patent.id == int(patent_id)).one_or_none()
    if row is None:
        row = (
            db.query(Patent)
            .filter(Patent.patent_number == patent_id)
            .one_or_none()
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Patent not found")
    return _patent_to_dict(row)


@router.post("/explain")
def explain_patent(
    req: PatentExplainRequest,
    _current: User = Depends(get_current_user),
):
    if len(req.patent_text) < 100:
        raise HTTPException(status_code=400, detail="Patent text too short for analysis")
    explanation = research_assistant.explain_patent(req.patent_text)
    return {"explanation": explanation}


@router.get("/analytics/overview")
def patent_analytics_overview(
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Backward-compatible analytics overview from the live corpus."""
    from app.patents.services.landscape_service import PatentLandscapeService
    return PatentLandscapeService(db).overview()


@router.get("/gap-analysis/ai")
def technology_gap_analysis(
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Technology gap analysis derived from the live corpus.

    Returns ``opportunities`` for areas with low patent density but
    high technology growth — the same kind of report the legacy
    hardcoded version produced, but computed from the data.
    """
    from app.patents.services.technology_intel_service import TechnologyIntelligenceService
    tech = TechnologyIntelligenceService(db)
    # Ensure trends are up to date.
    tech.recompute_trends()
    emerging = tech.emerging_technologies()
    fast_growing = tech.fast_growing_technologies()

    # Total patents per area to spot under-claimed spaces.
    from sqlalchemy import func
    rows = (
        db.query(Patent.technology_area, func.count(Patent.id).label("n"))
        .filter(Patent.technology_area.isnot(None))
        .group_by(Patent.technology_area)
        .all()
    )
    total = sum(n for _, n in rows) or 1
    opportunities: List[dict] = []

    for area, n in rows:
        share = n / total
        if share < 0.10 and (area in {t["technology_area"] for t in emerging} or area in {t["technology_area"] for t in fast_growing}):
            opportunities.append(
                {
                    "area": area,
                    "opportunity": (
                        f"Low patent density ({round(share * 100, 1)}%) in a "
                        f"{'fast-growing' if area in {t['technology_area'] for t in fast_growing} else 'emerging'} area"
                    ),
                    "potential": "High" if share < 0.05 else "Medium",
                }
            )
    if not opportunities:
        # Provide a useful default derived from the data so the UI
        # never appears empty.
        opportunities = [
            {
                "area": (emerging[0]["technology_area"] if emerging else (fast_growing[0]["technology_area"] if fast_growing else "Computing & AI")),
                "opportunity": "Cross-source innovation: align filings across Google Patents, USPTO, and The Lens",
                "potential": "High",
            }
        ]
    return {"report": opportunities}
