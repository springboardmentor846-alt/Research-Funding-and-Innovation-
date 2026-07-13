from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import role_required

from app.models.user import User
from app.models.proposal import Proposal
from app.models.funding import FundingOpportunity

router = APIRouter()


@router.get("/innovation/dashboard")
def innovation_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Innovation Manager"))
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    total_users = db.query(User).count()
    total_proposals = db.query(Proposal).count()
    total_funding = db.query(FundingOpportunity).count()

    approved = db.query(Proposal).filter(
        Proposal.status.ilike("approved")
    ).count()

    pending = db.query(Proposal).filter(
        Proposal.status.ilike("pending")
    ).count()

    return {
        "Innovation Manager": user.name,
        "Organization": user.organization,
        "Total Users": total_users,
        "Funding Opportunities": total_funding,
        "Total Proposals": total_proposals,
        "Approved Proposals": approved,
        "Pending Proposals": pending
    }