from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.research_profile import ResearchProfile
from app.models.user import User
from app.schemas.research_profile import (
    ResearchProfileCreate,
    ResearchProfileResponse,
)

router = APIRouter(
    prefix="/profile",
    tags=["Research Profile"]
)


@router.post("/", response_model=ResearchProfileResponse)
def create_profile(
    profile: ResearchProfileCreate,
    db: Session = Depends(get_db)
):
    # For now, use the first user.
    # Later, we'll replace this with the logged-in JWT user.
    user = db.query(User).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_profile = ResearchProfile(
        user_id=user.id,
        research_domain=profile.research_domain,
        keywords=profile.keywords,
        publications=profile.publications,
        patents=profile.patents,
        technology_area=profile.technology_area,
        organization=profile.organization,
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile


@router.get("/", response_model=ResearchProfileResponse)
def get_profile(db: Session = Depends(get_db)):
    profile = db.query(ResearchProfile).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile


@router.put("/", response_model=ResearchProfileResponse)
def update_profile(
    profile: ResearchProfileCreate,
    db: Session = Depends(get_db)
):
    existing_profile = db.query(ResearchProfile).first()

    if not existing_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    existing_profile.research_domain = profile.research_domain
    existing_profile.keywords = profile.keywords
    existing_profile.publications = profile.publications
    existing_profile.patents = profile.patents
    existing_profile.technology_area = profile.technology_area
    existing_profile.organization = profile.organization

    db.commit()
    db.refresh(existing_profile)

    return existing_profile