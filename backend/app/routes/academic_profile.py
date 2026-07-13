from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_token

from app.models.user import User
from app.models.academic_profile import AcademicProfile

from app.schemas.academic_profile import AcademicProfileCreate

router = APIRouter(
    tags=["Academic Profile"]
)

@router.post("/academic-profile")
def create_academic_profile(
    profile: AcademicProfileCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    existing = db.query(AcademicProfile).filter(
        AcademicProfile.user_id == user.id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Academic Profile Already Exists"
        )

    academic = AcademicProfile(
        user_id=user.id,
        highest_degree=profile.highest_degree,
        university=profile.university,
        department=profile.department,
        designation=profile.designation,
        years_experience=profile.years_experience
    )

    db.add(academic)
    db.commit()
    db.refresh(academic)

    return {
        "message": "Academic Profile Created Successfully",
        "academic_profile_id": academic.id
    }


@router.get("/academic-profile")
def get_academic_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    profile = db.query(AcademicProfile).filter(
        AcademicProfile.user_id == user.id
    ).first()

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Academic Profile Not Found"
        )

    return profile


@router.put("/academic-profile")
def update_academic_profile(
    profile: AcademicProfileCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    academic = db.query(AcademicProfile).filter(
        AcademicProfile.user_id == user.id
    ).first()

    if academic is None:
        raise HTTPException(
            status_code=404,
            detail="Academic Profile Not Found"
        )

    academic.highest_degree = profile.highest_degree
    academic.university = profile.university
    academic.department = profile.department
    academic.designation = profile.designation
    academic.years_experience = profile.years_experience

    db.commit()
    db.refresh(academic)

    return {
        "message": "Academic Profile Updated Successfully"
    }


@router.delete("/academic-profile")
def delete_academic_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    academic = db.query(AcademicProfile).filter(
        AcademicProfile.user_id == user.id
    ).first()

    if academic is None:
        raise HTTPException(
            status_code=404,
            detail="Academic Profile Not Found"
        )

    db.delete(academic)
    db.commit()

    return {
        "message": "Academic Profile Deleted Successfully"
    }