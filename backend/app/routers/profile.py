from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app import schemas, crud

router = APIRouter(
    prefix="/profile",
    tags=["Research Profile"]
)


@router.post("/", response_model=schemas.ResearchProfileResponse)
def create_profile(
    profile: schemas.ResearchProfileCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return crud.create_profile(db, profile, current_user)


@router.get("/", response_model=schemas.ResearchProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    profile = crud.get_profile(db, current_user)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile


@router.put("/", response_model=schemas.ResearchProfileResponse)
def update_profile(
    profile: schemas.ResearchProfileUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    updated = crud.update_profile(db, profile, current_user)

    if not updated:
        raise HTTPException(status_code=404, detail="Profile not found")

    return updated


@router.delete("/")
def delete_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    deleted = crud.delete_profile(db, current_user)

    if not deleted:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {
        "message": "Profile deleted successfully"
    }