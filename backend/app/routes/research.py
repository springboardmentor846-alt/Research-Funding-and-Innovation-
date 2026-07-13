from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.research_profile import ResearchProfile
from app.models.user import User
from app.schemas.research_profile import ResearchProfileCreate
from app.auth import verify_token

router = APIRouter(
    tags=["Research Profile"]
)


@router.post("/research-profile")
def create_research_profile(
    profile: ResearchProfileCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(User.email == current_user["sub"]).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_profile = (
        db.query(ResearchProfile)
        .filter(ResearchProfile.user_id == user.id)
        .first()
    )

    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="Research Profile already exists"
        )

    new_profile = ResearchProfile(
        user_id=user.id,
        research_domain=profile.research_domain,
        keywords=profile.keywords,
        publications=profile.publications,
        patents=profile.patents,
        technology_area=profile.technology_area,
        organization=profile.organization,
        experience=profile.experience
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return {
        "message": "Research Profile Created Successfully",
        "profile_id": new_profile.id
    }

@router.get("/research-profile")
def get_research_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    try:

        user = db.query(User).filter(
            User.email == current_user["sub"]
        ).first()

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        profile = (
            db.query(ResearchProfile)
            .filter(
                ResearchProfile.user_id == user.id
            )
            .first()
        )

        if not profile:

            return {
                "success": False,
                "message": "Research profile not found"
            }

        return {
            "success": True,
            "data": {
                "id": profile.id,
                "research_domain": profile.research_domain,
                "organization": profile.organization,
                "publications": profile.publications,
                "patents": profile.patents,
                "experience": profile.experience,
                "technology_area": profile.technology_area,
                "keywords": profile.keywords
            }
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }

@router.put("/research-profile")
def update_research_profile(
    profile: ResearchProfileCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    existing_profile = db.query(
        ResearchProfile
    ).filter(
        ResearchProfile.user_id == user.id
    ).first()

    if not existing_profile:
        raise HTTPException(
            status_code=404,
            detail="Research Profile not found"
        )

    existing_profile.research_domain = profile.research_domain
    existing_profile.keywords = profile.keywords
    existing_profile.publications = profile.publications
    existing_profile.patents = profile.patents
    existing_profile.technology_area = profile.technology_area
    existing_profile.organization = profile.organization
    existing_profile.experience = profile.experience

    db.commit()
    db.refresh(existing_profile)

    return {
        "success": True,
        "message": "Research Profile Updated Successfully",
        "data": existing_profile
    }

@router.delete("/research-profile")
def delete_research_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    profile = db.query(
        ResearchProfile
    ).filter(
        ResearchProfile.user_id == user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Research Profile not found"
        )

    db.delete(profile)
    db.commit()

    return {
        "success": True,
        "message": "Research Profile Deleted Successfully"
    }