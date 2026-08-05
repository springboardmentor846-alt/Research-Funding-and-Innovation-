from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import (
    get_db,
    require_role,
)

from app.models.startup import Startup
from app.models.user import User

from app.schemas.startup import (
    StartupCreate,
    StartupUpdate,
    StartupResponse,
)

from app.dependencies import get_current_user

router = APIRouter(
    prefix="/startup",
    tags=["Startup Profile"],
)


# =====================================================
# Create Startup Profile
# =====================================================

@router.post(
    "/profile",
    response_model=StartupResponse,
)
def create_profile(
    data: StartupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("startup_founder")
    ),
):

    existing = db.scalar(
        select(Startup).where(
            Startup.user_id == current_user.id
        )
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Startup profile already exists",
        )

    startup = Startup(
        user_id=current_user.id,
        **data.model_dump()
    )

    db.add(startup)
    db.commit()
    db.refresh(startup)

    return startup


# =====================================================
# Get Startup Profile
# =====================================================

@router.get(
    "/profile",
    response_model=StartupResponse,
)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("startup_founder")
    ),
):

    startup = db.scalar(
        select(Startup).where(
            Startup.user_id == current_user.id
        )
    )

    if startup is None:
        raise HTTPException(
            status_code=404,
            detail="Startup profile not found",
        )

    return startup


# =====================================================
# Update Startup Profile
# =====================================================

@router.put(
    "/profile",
    response_model=StartupResponse,
)
def update_profile(
    data: StartupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("startup_founder")
    ),
):

    startup = db.scalar(
        select(Startup).where(
            Startup.user_id == current_user.id
        )
    )

    if startup is None:
        raise HTTPException(
            status_code=404,
            detail="Startup profile not found",
        )

    update_data = data.model_dump()

    for field, value in update_data.items():
        setattr(startup, field, value)

    db.commit()
    db.refresh(startup)

    return startup


# =====================================================
# Delete Startup Profile
# =====================================================

@router.delete("/profile")
def delete_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("startup_founder")
    ),
):

    startup = db.scalar(
        select(Startup).where(
            Startup.user_id == current_user.id
        )
    )

    if startup is None:
        raise HTTPException(
            status_code=404,
            detail="Startup profile not found",
        )

    db.delete(startup)
    db.commit()

    return {
        "message": "Startup profile deleted successfully"
    }