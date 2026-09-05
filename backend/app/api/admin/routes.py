from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.core.security import require_role
from app.models.user import User
from app.models.research_profile import ResearchProfile
from app.models.publication import Publication
from app.models.patent import Patent
from app.models.funding import FundingOpportunity
from app.models.startup import Startup
from app.models.collaboration_request import CollaborationRequest
from app.models.password_reset_token import PasswordResetToken

router = APIRouter()

ALLOWED_ROLES = {"researcher", "startup_founder", "innovation_manager", "admin"}


class UserRoleUpdate(BaseModel):
    role: str = Field(min_length=1, max_length=50)


@router.get("/users")
def list_users(
    search: Optional[str] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"])),
):
    query = db.query(User)

    if role:
        query = query.filter(User.role == role)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter((User.name.ilike(term)) | (User.email.ilike(term)))

    users = query.all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
        }
        for u in users
    ]


@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"])),
):
    if data.role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Allowed roles: {', '.join(sorted(ALLOWED_ROLES))}",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = data.role
    db.commit()
    db.refresh(user)
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"])),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Clean up dependent records first, since foreign keys don't cascade
    # automatically — this keeps the delete from failing with an
    # integrity error when the user has related data.
    profile = db.query(ResearchProfile).filter(ResearchProfile.user_id == user.id).first()
    if profile:
        db.query(Publication).filter(Publication.profile_id == profile.id).delete()
        db.query(Patent).filter(Patent.profile_id == profile.id).delete()
        db.delete(profile)

    db.query(Startup).filter(Startup.user_id == user.id).delete()
    db.query(CollaborationRequest).filter(
        (CollaborationRequest.sender_id == user.id) | (CollaborationRequest.receiver_id == user.id)
    ).delete()
    db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).delete()

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}


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