from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.dependencies import get_current_user
from app.services import recommendation_service, eligibility_service

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/{user_id}")
def get_recommendations(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return top 10 funding recommendations for a researcher
    based on their profile, keywords, and publication history.
    """
    # Users can only view their own recommendations unless admin
    if current_user["id"] != user_id and current_user["role"] != "administrator":
        raise HTTPException(status_code=403, detail="Access denied")

    recommendations = recommendation_service.get_recommendations(db, user_id)
    return {
        "user_id": user_id,
        "total": len(recommendations),
        "recommendations": recommendations,
    }


@router.get("/eligibility/{funding_id}")
def check_grant_eligibility(
    funding_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Check eligibility of the current user for a specific funding opportunity.
    Returns Eligible / Partially Eligible / Not Eligible with match percentage.
    """
    result = eligibility_service.check_eligibility(db, current_user["id"], funding_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
