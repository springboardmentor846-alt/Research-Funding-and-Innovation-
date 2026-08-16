from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import FundingOpportunity, Publication, Patent, TechTrend, InnovationScore, CommercializationOpportunity, User

router = APIRouter(prefix="/dashboards", tags=["Dashboards & Analytics"])

@router.get("/overview")
def get_dashboard_overview(db: Session = Depends(get_db)):
    total_funding = db.query(FundingOpportunity).count()
    sum_funding = db.query(FundingOpportunity).all()
    total_funding_usd = sum(g.amount for g in sum_funding)

    total_publications = db.query(Publication).count()
    total_patents = db.query(Patent).count()
    total_trends = db.query(TechTrend).count()
    total_commercial = db.query(CommercializationOpportunity).count()

    scores = db.query(InnovationScore).all()
    avg_score = round(sum(s.overall_score for s in scores) / len(scores), 1) if scores else 78.4

    # Chart datasets
    funding_by_type = {}
    for g in sum_funding:
        funding_by_type[g.grant_type] = funding_by_type.get(g.grant_type, 0) + 1

    funding_chart = [{"category": k, "count": v} for k, v in funding_by_type.items()]

    recent_scores = [
        {
            "name": s.entity_name,
            "type": s.entity_type,
            "score": s.overall_score,
            "novelty": s.novelty_score,
            "market": s.market_potential
        } for s in scores[:5]
    ]

    return {
        "kpis": {
            "total_funding_grants": total_funding,
            "total_funding_usd": f"${total_funding_usd/1e6:.1f}M",
            "total_publications": total_publications,
            "total_patents": total_patents,
            "emerging_technologies": total_trends,
            "average_innovation_score": avg_score,
            "commercial_opportunities": total_commercial
        },
        "funding_distribution": funding_chart,
        "recent_innovation_scores": recent_scores
    }
