from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import role_required

from app.models.user import User
from app.models.proposal import Proposal
from app.models.funding import FundingOpportunity

router = APIRouter()


@router.get("/startup/dashboard")
def startup_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Startup Founder"))
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    total_proposals = db.query(Proposal).filter(
        Proposal.user_id == user.id
    ).count()

    funding_count = db.query(FundingOpportunity).count()

    return {
        "Startup Founder": user.name,
        "Organization": user.organization,
        "Email": user.email,
        "Available Funding": funding_count,
        "Submitted Proposals": total_proposals,
        "Innovation Score": 0,
        "Commercialization Opportunities": 0
    }