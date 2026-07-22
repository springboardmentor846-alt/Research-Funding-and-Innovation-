from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.innovation import InnovationResponse
from app.services.innovation_service import calculate_innovation

router = APIRouter(
    prefix="/innovation",
    tags=["Innovation Intelligence"]
)


# ==========================================================
# Innovation Score API
# ==========================================================
@router.get("/score", response_model=InnovationResponse)
def get_innovation_score(
    db: Session = Depends(get_db)
):
    result = calculate_innovation(db)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Required data not found. Please add Patent, Technology and Research Profile data."
        )

    return result