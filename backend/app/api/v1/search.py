"""Search endpoints (Elasticsearch + FAISS semantic)."""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.orm import Session

from app.db import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.models.publication import Publication
from app.models.funding import Funding
from app.search.elasticsearch_store import search_engine
from app.search.faiss_store import get_store
from app.ai.recommender import funding_recommender
from app.ai.text_preprocessing import TextPreprocessor

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/publications")
def search_publications(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Keyword search over publications (Elasticsearch with in-DB fallback)."""
    results = search_engine.search("publications", q, fields=["title", "abstract", "keywords"], size=page_size)
    if not results:
        from sqlalchemy import or_
        term = f"%{q}%"
        items = (
            db.query(Publication)
            .filter(
                or_(
                    Publication.title.ilike(term),
                    Publication.abstract.ilike(term),
                    Publication.keywords.ilike(term),
                )
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        results = [
            {
                "id": p.id,
                "title": p.title,
                "abstract": p.abstract,
                "keywords": p.keywords,
                "doi": p.doi,
                "citation_count": p.citation_count,
            }
            for p in items
        ]
    return {"query": q, "results": results, "count": len(results)}


@router.get("/funding")
def search_funding(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Keyword search over funding opportunities."""
    results = search_engine.search("funding", q, fields=["title", "description", "keywords"], size=page_size)
    if not results:
        from sqlalchemy import or_
        term = f"%{q}%"
        items = (
            db.query(Funding)
            .filter(
                Funding.is_active == True,
                or_(
                    Funding.title.ilike(term),
                    Funding.description.ilike(term),
                    Funding.keywords.ilike(term),
                ),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        results = [
            {
                "id": f.id,
                "title": f.title,
                "description": f.description,
                "organization": f.organization,
                "research_domain": f.research_domain,
            }
            for f in items
        ]
    return {"query": q, "results": results, "count": len(results)}


@router.post("/semantic")
def semantic_search(
    q: str = Query(..., min_length=1),
    collection: str = Query("publications", pattern="^(publications|funding|patents)$"),
    top_k: int = Query(10, ge=1, le=50),
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """FAISS-based semantic search across publications / funding / patents."""
    store = get_store(collection)
    store.clear()
    pp = TextPreprocessor()

    if collection == "publications":
        items = db.query(Publication).all()
        for p in items:
            text = " ".join([p.title or "", p.abstract or "", p.keywords or ""])
            store.add(str(p.id), text, {"id": p.id, "title": p.title, "type": "publication"})
    elif collection == "funding":
        items = db.query(Funding).filter(Funding.is_active == True).all()
        for f in items:
            text = " ".join([f.title or "", f.description or "", f.keywords or ""])
            store.add(str(f.id), text, {"id": f.id, "title": f.title, "type": "funding"})
    else:
        # patents: empty for now (placeholder for external integration)
        return {"query": q, "results": [], "count": 0}

    store.build()
    raw = store.search(q, top_k=top_k)
    return {
        "query": q,
        "collection": collection,
        "results": [
            {"score": round(score, 4), **payload} for (_id, score, payload) in raw
        ],
        "count": len(raw),
    }
