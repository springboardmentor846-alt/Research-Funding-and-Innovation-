from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.grant import Grant
from app.schemas.grant import GrantCreate
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/grants",
    tags=["Grants"]
)
@router.post("/")
def create_grant(
    grant: GrantCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if current_user["role"] not in ("administrator", "innovation_manager"):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions"
        )

    new_grant = Grant(
        title=grant.title,
        description=grant.description,
        funding_amount=grant.funding_amount,
        deadline=grant.deadline,
        organization=grant.organization,
        eligibility=grant.eligibility,
        status="Open"
    )

    db.add(new_grant)
    db.commit()
    db.refresh(new_grant)

    return new_grant
@router.get("/")
def get_all_grants(db: Session = Depends(get_db)):
    return db.query(Grant).all()
@router.get("/{grant_id}")
def get_grant(grant_id: int, db: Session = Depends(get_db)):

    grant = db.query(Grant).filter(
        Grant.id == grant_id
    ).first()

    if not grant:
        raise HTTPException(
            status_code=404,
            detail="Grant not found"
        )

    return grant
@router.put("/{grant_id}")
def update_grant(
    grant_id: int,
    grant: GrantCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if current_user["role"] not in ("administrator", "innovation_manager"):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions"
        )

    db_grant = db.query(Grant).filter(
        Grant.id == grant_id
    ).first()

    if not db_grant:
        raise HTTPException(
            status_code=404,
            detail="Grant not found"
        )

    db_grant.title = grant.title
    db_grant.description = grant.description
    db_grant.funding_amount = grant.funding_amount
    db_grant.deadline = grant.deadline
    db_grant.organization = grant.organization
    db_grant.eligibility = grant.eligibility

    db.commit()
    db.refresh(db_grant)

    return db_grant
@router.delete("/{grant_id}")
def delete_grant(
    grant_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if current_user["role"] not in ("administrator", "innovation_manager"):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions"
        )

    grant = db.query(Grant).filter(
        Grant.id == grant_id
    ).first()

    if not grant:
        raise HTTPException(
            status_code=404,
            detail="Grant not found"
        )

    db.delete(grant)
    db.commit()

    return {"message": "Grant deleted successfully"}