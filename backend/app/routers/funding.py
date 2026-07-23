from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas
from app.auth import get_current_user

router = APIRouter(
    prefix="/funding",
    tags=["Funding Opportunities"]
)


@router.post("/", response_model=schemas.FundingOpportunityResponse)
def create_funding(
    funding: schemas.FundingOpportunityCreate,
    db: Session = Depends(get_db)
):
    return crud.create_funding(db, funding)


@router.get("/", response_model=list[schemas.FundingOpportunityResponse])
def get_all_funding(
    db: Session = Depends(get_db)
):
    return crud.get_all_funding(db)


@router.get(
    "/recommendations",
    response_model=list[schemas.FundingOpportunityResponse]
)
def funding_recommendations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return crud.get_funding_recommendations(
        db,
        current_user
    )

@router.get(
    "/match",
    response_model=list[schemas.GrantMatchResponse]
)
def grant_matching(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return crud.get_grant_matches(
        db,
        current_user
    )
    
@router.get("/{funding_id}", response_model=schemas.FundingOpportunityResponse)
def get_funding(
    funding_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_funding(db, funding_id)


@router.put("/{funding_id}", response_model=schemas.FundingOpportunityResponse)
def update_funding(
    funding_id: int,
    funding: schemas.FundingOpportunityUpdate,
    db: Session = Depends(get_db)
):
    return crud.update_funding(db, funding_id, funding)


@router.delete("/{funding_id}")
def delete_funding(
    funding_id: int,
    db: Session = Depends(get_db)
):
    return crud.delete_funding(db, funding_id)