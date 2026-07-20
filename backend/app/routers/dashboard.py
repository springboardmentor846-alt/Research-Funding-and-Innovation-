from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role

from app.models.user import User
from app.models.research_profile import ResearchProfile

from app.services.dashboard_service import (
    get_dashboard_statistics,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("")
def dashboard(
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):

    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Research profile not found."
        )

    dashboard_data = get_dashboard_statistics(
        db,
        profile
    )

    return {
        "researcher": current_user.full_name,

        "profile": {
            "qualification": profile.highest_qualification,
            "organization": profile.organization_name,
            "position": profile.current_position
        },

        **dashboard_data
    }