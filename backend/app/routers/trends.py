from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.models.user import User
from app.models.research_profile import ResearchProfile

from app.services.trend_service import publication_statistics

router = APIRouter(
    prefix="/trends",
    tags=["Research Trends"]
)


@router.get("/publications")
def publication_trends(
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

    return publication_statistics(
        db,
        profile
    )