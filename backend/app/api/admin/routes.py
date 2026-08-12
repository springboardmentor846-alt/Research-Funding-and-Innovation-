from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import require_role
from app.models.user import User
from app.models.research_profile import ResearchProfile
from app.models.publication import Publication
from app.models.patent import Patent
from app.models.funding import FundingOpportunity

router = APIRouter()


@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"])),
):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
        }
        for u in users
    ]


@router.get("/stats")
def platform_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"])),
):
    total_users = db.query(User).count()
    total_profiles = db.query(ResearchProfile).count()
    total_publications = db.query(Publication).count()
    total_patents = db.query(Patent).count()
    total_funding = db.query(FundingOpportunity).count()

    role_counts = {}
    for u in db.query(User).all():
        role_counts[u.role] = role_counts.get(u.role, 0) + 1

    return {
        "total_users": total_users,
        "total_profiles": total_profiles,
        "total_publications": total_publications,
        "total_patents": total_patents,
        "total_funding_opportunities": total_funding,
        "users_by_role": role_counts,
    }