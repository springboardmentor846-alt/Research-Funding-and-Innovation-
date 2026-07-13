from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_token,role_required

from app.models.user import User
from app.models.research_profile import ResearchProfile
from app.models.funding import FundingOpportunity
from app.models.proposal import Proposal

router = APIRouter(
    tags=["Dashboard"]
)
@router.get("/admin/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Admin"))
):

    total_users = db.query(User).count()

    total_profiles = db.query(ResearchProfile).count()

    total_funding = db.query(FundingOpportunity).count()

    total_proposals = db.query(Proposal).count()

    approved = db.query(Proposal).filter(
        Proposal.status == "Approved"
    ).count()

    pending = db.query(Proposal).filter(
        Proposal.status == "Pending"
    ).count()

    rejected = db.query(Proposal).filter(
        Proposal.status == "Rejected"
    ).count()

    return {
        "Total Users": total_users,
        "Total Research Profiles": total_profiles,
        "Total Funding Opportunities": total_funding,
        "Total Proposals": total_proposals,
        "Approved Proposals": approved,
        "Pending Proposals": pending,
        "Rejected Proposals": rejected
    }