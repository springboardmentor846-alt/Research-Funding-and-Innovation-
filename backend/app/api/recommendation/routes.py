from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.crud.user import get_user_by_email
from app.crud.research_profile import get_profile_by_user_id
from app.services import recommendation_service

router = APIRouter()


def _get_current_profile(db: Session, current_user: dict):
    user = get_user_by_email(db, current_user.get("sub"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = get_profile_by_user_id(db, user.id)
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Complete your research profile first to get recommendations",
        )
    return profile


@router.get("/funding")
def recommended_funding(
    top_n: int = 5,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Semantically ranked funding opportunities for the current user's profile."""
    profile = _get_current_profile(db, current_user)
    return recommendation_service.recommend_funding(db, profile, top_n=top_n)


@router.get("/collaborators")
def recommended_collaborators(
    top_n: int = 5,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Semantically ranked potential collaborators for the current user's profile."""
    profile = _get_current_profile(db, current_user)
    return recommendation_service.recommend_collaborators(db, profile, top_n=top_n)