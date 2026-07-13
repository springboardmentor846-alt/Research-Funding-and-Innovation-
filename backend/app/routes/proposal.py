from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_token,role_required

from app.models.user import User
from app.models.proposal import Proposal

from app.schemas.proposal import ProposalCreate

router = APIRouter(
    tags=["Proposal"]
)


@router.post("/proposal")
def submit_proposal(
    proposal: ProposalCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    new_proposal = Proposal(
        user_id=user.id,
        funding_id=proposal.funding_id,
        title=proposal.title,
        abstract=proposal.abstract,
        status="Pending"
    )

    db.add(new_proposal)
    db.commit()
    db.refresh(new_proposal)

    return {
        "message": "Proposal Submitted Successfully",
        "proposal_id": new_proposal.id
    }

@router.get("/proposals")
def view_all_proposals(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    proposals = db.query(Proposal).all()

    return proposals
@router.get("/my-proposals")
def my_proposals(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    proposals = db.query(Proposal).filter(
        Proposal.user_id == user.id
    ).all()

    return proposals

@router.put("/proposal/{proposal_id}/status")
def update_proposal_status(
    proposal_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Admin"))):

    proposal = db.query(Proposal).filter(
        Proposal.id == proposal_id
    ).first()

    if proposal is None:
        raise HTTPException(
            status_code=404,
            detail="Proposal Not Found"
        )
    
    status=status.capitalize()
    allowed_status = ["Pending", "Approved", "Rejected"]

    if status not in allowed_status:
        raise HTTPException(
            status_code=400,
            detail="Status must be Pending, Approved or Rejected"
            )

    proposal.status = status
    db.commit()
    db.refresh(proposal)

    return {
        "message": "Proposal Status Updated Successfully",
        "status": proposal.status
    }
@router.get("/proposal/{proposal_id}")
def get_proposal(proposal_id: int, db: Session = Depends(get_db)):
    return db.query(Proposal).filter(Proposal.id == proposal_id).first()