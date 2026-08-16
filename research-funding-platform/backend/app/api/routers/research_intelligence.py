from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Publication
from app.schemas.schemas import PublicationRead, PublicationCreate
from app.services.ai_service_interface import ai_service
from typing import List, Optional

router = APIRouter(prefix="/research-intelligence", tags=["Research Intelligence"])

@router.get("/publications", response_model=List[PublicationRead])
def get_publications(
    query: Optional[str] = None,
    journal: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    q = db.query(Publication)
    if query:
        search_pattern = f"%{query}%"
        q = q.filter(
            (Publication.title.ilike(search_pattern)) |
            (Publication.authors.ilike(search_pattern)) |
            (Publication.abstract.ilike(search_pattern)) |
            (Publication.keywords.ilike(search_pattern))
        )
    if journal:
        q = q.filter(Publication.journal.ilike(f"%{journal}%"))

    return q.offset(skip).limit(limit).all()

@router.get("/analytics")
def get_research_analytics(db: Session = Depends(get_db)):
    pubs = db.query(Publication).all()
    total_pubs = len(pubs)
    total_citations = sum(p.citations_count for p in pubs)
    avg_impact = round(sum(p.impact_factor for p in pubs) / total_pubs, 2) if total_pubs > 0 else 0.0

    domain_counts = {}
    for p in pubs:
        kw_list = [k.strip() for k in (p.keywords or "Artificial Intelligence").split(",")]
        for kw in kw_list:
            domain_counts[kw] = domain_counts.get(kw, 0) + 1

    top_topics = sorted([{"topic": k, "count": v} for k, v in domain_counts.items()], key=lambda x: x["count"], reverse=True)[:6]

    return {
        "total_publications": total_pubs,
        "total_citations": total_citations,
        "average_impact_factor": avg_impact,
        "top_topics": top_topics
    }

@router.post("/analyze-paper")
async def analyze_paper_abstract(payload: dict):
    title = payload.get("title", "Quantum Machine Learning in Drug Discovery")
    abstract = payload.get("abstract", "This paper introduces a hybrid quantum-classical neural network architecture designed to simulate complex molecular interactions with quadratic speedups over traditional HPC approaches.")
    result = await ai_service.generate_research_summary(title, abstract)
    return result

@router.post("/publications", response_model=PublicationRead, status_code=status.HTTP_201_CREATED)
def create_publication(pub_in: PublicationCreate, db: Session = Depends(get_db)):
    pub = Publication(**pub_in.model_dump())
    db.add(pub)
    db.commit()
    db.refresh(pub)
    return pub
