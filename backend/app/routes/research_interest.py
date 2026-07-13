from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_token

from app.models.user import User
from app.models.research_interest import ResearchInterest

from app.schemas.research_interest import ResearchInterestCreate


router = APIRouter(
    tags=["Research Interest"]
)
@router.post("/research-interest")
def add_interest(
    data: ResearchInterestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    interest = ResearchInterest(
        user_id=user.id,
        interest=data.interest
    )

    db.add(interest)
    db.commit()
    db.refresh(interest)

    return {
        "message": "Research Interest Added Successfully",
        "interest_id": interest.id
    }


@router.get("/research-interests")
def get_interests(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    return db.query(ResearchInterest).filter(
        ResearchInterest.user_id == user.id
    ).all()


@router.put("/research-interest/{interest_id}")
def update_interest(
    interest_id: int,
    data: ResearchInterestCreate,
    db: Session = Depends(get_db)
):

    interest = db.query(ResearchInterest).filter(
        ResearchInterest.id == interest_id
    ).first()

    if interest is None:
        raise HTTPException(
            status_code=404,
            detail="Research Interest Not Found"
        )

    interest.interest = data.interest

    db.commit()
    db.refresh(interest)

    return {
        "message": "Research Interest Updated Successfully"
    }


@router.delete("/research-interest/{interest_id}")
def delete_interest(
    interest_id: int,
    db: Session = Depends(get_db)
):

    interest = db.query(ResearchInterest).filter(
        ResearchInterest.id == interest_id
    ).first()

    if interest is None:
        raise HTTPException(
            status_code=404,
            detail="Research Interest Not Found"
        )

    db.delete(interest)
    db.commit()

    return {
        "message": "Research Interest Deleted Successfully"
    }