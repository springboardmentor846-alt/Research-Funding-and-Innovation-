from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.commercialization import CommercializationResponse
from app.services.commercialization_service import commercialization_analysis

router = APIRouter(
    prefix="/commercialization",
    tags=["Commercialization Intelligence"]
)


# ==========================================================
# Commercialization Recommendation
# ==========================================================
@router.get(
    "/recommendation",
    response_model=CommercializationResponse
)
def get_commercialization_recommendation(
    db: Session = Depends(get_db)
):
    result = commercialization_analysis(db)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Patent, Technology or Research Profile data not found."
        )

    return result