from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.models.user import User

from app.services.orcid_service import (
    get_orcid_profile
)

router = APIRouter(
    prefix="/orcid",
    tags=["ORCID"]
)


@router.get("/{orcid_id}")
def fetch_orcid_profile(
    orcid_id: str,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):

    try:

        profile = get_orcid_profile(
            orcid_id
        )

        return profile

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )