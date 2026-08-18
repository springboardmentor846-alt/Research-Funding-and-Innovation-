"""Trend analytics endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.models.publication import Publication
from app.ai.trends import trend_analyzer

router = APIRouter(prefix="/trends", tags=["Trends"])


@router.get("/me")
def my_trends(current: User = Depends(get_current_user)):
    """Personal research trends for the current user."""
    pubs = current.publications
    payload = {
        "trending_keywords": trend_analyzer.extract_trending_keywords(pubs, top_n=20),
        "domain_distribution": trend_analyzer.domain_distribution(pubs),
        "citation_trends": trend_analyzer.citation_trends(pubs),
        "research_growth": trend_analyzer.research_growth(pubs),
        "technology_evolution": trend_analyzer.technology_evolution(pubs),
    }
    # Best-effort: surface a single research-trend notification when
    # the personal trend snapshot is computed.  Idempotent via the
    # dedup_key (one per user per UTC day).
    try:
        from app.services.notification_service import notify_research_trend
        top_kw = (
            payload.get("trending_keywords") or []
        )
        topic = (
            (top_kw[0].get("keyword") if isinstance(top_kw[0], dict) else None)
            if top_kw
            else None
        )
        if topic:
            notify_research_trend(
                user=current,
                topic=topic,
                change_summary="A significant increase in activity has been detected",
            )
    except Exception:  # pragma: no cover - never break the response
        pass
    return payload


@router.get("/emerging-topics")
def emerging_topics(_current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Platform-wide emerging topics (across all users)."""
    all_pubs = db.query(Publication).all()
    return {
        "trending_keywords": trend_analyzer.extract_trending_keywords(all_pubs, top_n=30),
        "domain_distribution": trend_analyzer.domain_distribution(all_pubs),
        "research_growth": trend_analyzer.research_growth(all_pubs),
    }
