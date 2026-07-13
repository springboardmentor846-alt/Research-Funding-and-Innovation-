from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.research_trend import ResearchTrend
from app.schemas.research_trend import ResearchTrendCreate

router = APIRouter(tags=["Research Trends"])


@router.post("/research-trends")
def add_research_trend(
    trend: ResearchTrendCreate,
    db: Session = Depends(get_db)
):

    new_trend = ResearchTrend(
        title=trend.title,
        research_domain=trend.research_domain,
        publication_year=trend.publication_year,
        citation_count=trend.citation_count,
        hotspot_score=trend.hotspot_score,
        trend_level=trend.trend_level
    )

    db.add(new_trend)
    db.commit()
    db.refresh(new_trend)

    return {
        "message": "Research Trend Added Successfully",
        "trend_id": new_trend.id
    }

@router.get("/research-trends")
def get_all_research_trends(
    db: Session = Depends(get_db)
):

    trends = db.query(ResearchTrend).all()

    return trends

@router.get("/research-trends/publication/{year}")
def publication_trends(
    year: int,
    db: Session = Depends(get_db)
):

    trends = db.query(ResearchTrend).filter(
        ResearchTrend.publication_year == year
    ).all()

    return {
        "Publication Year": year,
        "Total Publications": len(trends),
        "Research Trends": trends
    }

@router.get("/research-trends/domain/{domain}")
def domain_trends(
    domain: str,
    db: Session = Depends(get_db)
):

    trends = db.query(ResearchTrend).filter(
        ResearchTrend.research_domain.ilike(f"%{domain}%")
    ).all()

    return {
        "Domain": domain,
        "Total Trends": len(trends),
        "Research Trends": trends
    }

@router.get("/research-trends/emerging")
def emerging_topics(
    db: Session = Depends(get_db)
):

    trends = db.query(ResearchTrend).filter(
        ResearchTrend.trend_level.ilike("High")
    ).all()

    return {
        "Emerging Topics": trends
    }

@router.get("/research-trends/hotspots")
def research_hotspots(
    db: Session = Depends(get_db)
):

    hotspots = db.query(ResearchTrend).filter(
        ResearchTrend.hotspot_score >= 80
    ).all()

    return {
        "Research Hotspots": hotspots
    }

@router.get("/research-trends/citation-analytics")
def citation_analytics(
    db: Session = Depends(get_db)
):

    total_papers = db.query(ResearchTrend).count()

    total_citations = db.query(
        func.sum(ResearchTrend.citation_count)
    ).scalar()

    average_citations = db.query(
        func.avg(ResearchTrend.citation_count)
    ).scalar()

    highest = db.query(ResearchTrend).order_by(
        ResearchTrend.citation_count.desc()
    ).first()

    return {
        "Total Papers": total_papers,
        "Total Citations": total_citations or 0,
        "Average Citations": round(average_citations or 0, 2),
        "Most Cited Research": highest
    }