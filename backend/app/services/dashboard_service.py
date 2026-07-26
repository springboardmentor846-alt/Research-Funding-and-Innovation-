from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.funding import FundingOpportunity
from app.models.publication import Publication
from app.models.profile import ResearcherProfile


def get_dashboard_stats(db: Session, user_id: int) -> dict:
    """Aggregate stats for the research intelligence dashboard."""
    total_publications = db.query(Publication).count()
    total_funding = db.query(FundingOpportunity).count()
    open_funding = db.query(FundingOpportunity).filter(
        FundingOpportunity.status == "Open"
    ).count()

    # Research domains count
    domains = (
        db.query(Publication.research_domain, func.count(Publication.id).label("count"))
        .group_by(Publication.research_domain)
        .order_by(func.count(Publication.id).desc())
        .limit(5)
        .all()
    )

    # Publication growth by year
    pub_growth = (
        db.query(Publication.year, func.count(Publication.id).label("count"))
        .group_by(Publication.year)
        .order_by(Publication.year)
        .all()
    )

    # Recent funding opportunities
    recent_funding = (
        db.query(FundingOpportunity)
        .order_by(FundingOpportunity.created_at.desc())
        .limit(5)
        .all()
    )

    # Funding by agency (for pie chart)
    funding_by_agency = (
        db.query(
            FundingOpportunity.agency,
            func.count(FundingOpportunity.id).label("count"),
            func.sum(FundingOpportunity.funding_amount).label("total_amount"),
        )
        .group_by(FundingOpportunity.agency)
        .order_by(func.count(FundingOpportunity.id).desc())
        .limit(8)
        .all()
    )

    # Funding amount trend by year (area chart)
    funding_trend = (
        db.query(
            func.extract("year", FundingOpportunity.deadline).label("year"),
            func.sum(FundingOpportunity.funding_amount).label("total"),
        )
        .group_by(func.extract("year", FundingOpportunity.deadline))
        .order_by(func.extract("year", FundingOpportunity.deadline))
        .all()
    )

    return {
        "stats": {
            "total_publications": total_publications,
            "total_funding_opportunities": total_funding,
            "open_funding": open_funding,
            "research_domains": len(domains),
        },
        "top_domains": [{"domain": d.research_domain, "count": d.count} for d in domains],
        "publication_growth": [{"year": p.year, "count": p.count} for p in pub_growth],
        "recent_opportunities": [
            {
                "id": f.id,
                "title": f.title,
                "agency": f.agency,
                "funding_amount": f.funding_amount,
                "deadline": str(f.deadline),
                "research_domain": f.research_domain,
            }
            for f in recent_funding
        ],
        "funding_by_agency": [
            {
                "agency": a.agency,
                "count": a.count,
                "total_amount": float(a.total_amount or 0),
            }
            for a in funding_by_agency
        ],
        "funding_amount_trend": [
            {"year": int(t.year), "total": float(t.total or 0)} for t in funding_trend
        ],
    }
