from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.models.research_profile import ResearchProfile
from app.models.funding_opportunity import FundingOpportunity
from app.models.research_trend import ResearchTrend

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/")
def dashboard(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    total_profiles = db.query(ResearchProfile).count()
    total_funding = db.query(FundingOpportunity).count()
    total_trends = db.query(ResearchTrend).count()

    return {
        "total_users": total_users,
        "total_profiles": total_profiles,
        "total_funding_opportunities": total_funding,
        "total_research_trends": total_trends,
    }