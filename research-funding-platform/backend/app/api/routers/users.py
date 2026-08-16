from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth_deps import get_current_user
from app.models.models import User, ResearchProfile
from app.schemas.schemas import UserRead, UserUpdate, ResearchProfileRead, ResearchProfileCreate
from typing import List

router = APIRouter(prefix="/users", tags=["Users & Research Profiles"])

@router.get("/me", response_model=UserRead)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserRead)
def update_user_profile(user_update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_update.full_name:
        current_user.full_name = user_update.full_name
    if user_update.organization:
        current_user.organization = user_update.organization
    if user_update.role:
        current_user.role = user_update.role
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/me/research-profile", response_model=ResearchProfileRead)
def get_user_research_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(ResearchProfile).filter(ResearchProfile.user_id == current_user.id).first()
    if not profile:
        profile = ResearchProfile(
            user_id=current_user.id,
            organization=current_user.organization,
            domains="Artificial Intelligence, Clean Energy",
            keywords="Deep Learning, Renewable Systems"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.put("/me/research-profile", response_model=ResearchProfileRead)
def update_user_research_profile(profile_in: ResearchProfileCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(ResearchProfile).filter(ResearchProfile.user_id == current_user.id).first()
    if not profile:
        profile = ResearchProfile(user_id=current_user.id)
        db.add(profile)

    for field, val in profile_in.model_dump(exclude_unset=True).items():
        setattr(profile, field, val)

    db.commit()
    db.refresh(profile)
    return profile
