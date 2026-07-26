# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from app.database.database import get_db
# from app.models.profile import ResearcherProfile
# from app.schemas.profile import ProfileCreate
# from app.auth.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.profile import ResearcherProfile
from app.schemas.profile import ProfileCreate
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


# -----------------------------
# Create Profile
# -----------------------------
@router.post("/")
def create_profile(
    profile: ProfileCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    existing_profile = db.query(ResearcherProfile).filter(
        ResearcherProfile.user_id == current_user["id"]
    ).first()

    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="Profile already exists"
        )

    new_profile = ResearcherProfile(
        user_id=current_user["id"],
        organization=profile.organization,
        designation=profile.designation,
        research_domain=profile.research_domain,
        keywords=profile.keywords,
        biography=profile.biography
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile


# -----------------------------
# Get Logged-in User Profile
# -----------------------------
@router.get("/me")
def my_profile(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    profile = db.query(ResearcherProfile).filter(
        ResearcherProfile.user_id == current_user["id"]
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return profile


# -----------------------------
# Admin Only Route
# -----------------------------
@router.get("/admin")
def admin_only(
    current_user=Depends(get_current_user)
):

    if current_user["role"] != "administrator":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can access this endpoint."
        )

    return {
        "message": "Welcome Administrator!"
    }


# -----------------------------
# Get Profile by User ID
# -----------------------------
@router.get("/{user_id}")
def get_profile(
    user_id: int,
    db: Session = Depends(get_db)
):

    profile = db.query(ResearcherProfile).filter(
        ResearcherProfile.user_id == user_id
    ).first()

    if not profile:
        return {"message": "Profile not found"}

    return profile


# -----------------------------
# Update Profile
# -----------------------------
@router.put("/")
def update_profile(
    profile: ProfileCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    db_profile = db.query(ResearcherProfile).filter(
        ResearcherProfile.user_id == current_user["id"]
    ).first()

    if not db_profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    db_profile.organization = profile.organization
    db_profile.designation = profile.designation
    db_profile.research_domain = profile.research_domain
    db_profile.keywords = profile.keywords
    db_profile.biography = profile.biography

    db.commit()
    db.refresh(db_profile)

    return db_profile


# -----------------------------
# Delete Profile
# -----------------------------
@router.delete("/")
def delete_profile(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    profile = db.query(ResearcherProfile).filter(
        ResearcherProfile.user_id == current_user["id"]
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    db.delete(profile)
    db.commit()

    return {
        "message": "Profile deleted successfully"
    }