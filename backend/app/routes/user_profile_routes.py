from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.utils.auth_dependency import get_current_user

from app.schemas.user_profile_schema import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
)

from app.services.user_profile_service import (
    create_profile,
    get_my_profile,
    update_profile,
    delete_profile,
)

router = APIRouter(
    prefix="/profile",
    tags=["User Profile"]
)


@router.post(
    "/create",
    response_model=UserProfileResponse
)
def create_user_profile(
    profile: UserProfileCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return create_profile(db, profile, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/me",
    response_model=UserProfileResponse
)
def get_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    profile = get_my_profile(db, current_user)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return profile


@router.put(
    "/update",
    response_model=UserProfileResponse
)
def update_user_profile(
    profile: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    updated = update_profile(db, profile, current_user)

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return updated


@router.delete("/delete")
def delete_user_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    deleted = delete_profile(db, current_user)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return deleted