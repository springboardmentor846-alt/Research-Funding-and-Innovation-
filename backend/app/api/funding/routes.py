from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.schemas.funding import FundingCreate, FundingResponse
from app.crud.funding import (
    create_funding,
    get_all_funding,
    get_funding_by_id,
    get_recommended_funding,
    search_funding,
    search_grants_gov,
)
from app.core.security import get_current_user, require_role
from app.core.limiter import limiter
from app.crud.user import get_user_by_email
from app.crud.research_profile import get_profile_by_user_id

router = APIRouter()


@router.post("/", response_model=FundingResponse)
def add_funding(
    data: FundingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"])),
):
    return create_funding(db, data)


@router.get("/", response_model=List[FundingResponse])
def list_funding(db: Session = Depends(get_db)):
    return get_all_funding(db)


@router.get("/recommended", response_model=List[FundingResponse])
def recommended_funding(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Create your research profile first")

    return get_recommended_funding(db, profile.research_domains, db_user.role)


@router.get("/search", response_model=List[FundingResponse])
def search_funding_opportunities(
    query: Optional[str] = None,
    domain: Optional[str] = None,
    db: Session = Depends(get_db),
):
    keyword = query or domain or ""
    return search_funding(db, keyword)


@router.get("/search-live")
@limiter.limit("10/minute")
def search_live_grants(
    request: Request,
    keyword: str,
    current_user: dict = Depends(get_current_user),
):
    return search_grants_gov(keyword)


@router.get("/{funding_id}", response_model=FundingResponse)
def get_funding(funding_id: int, db: Session = Depends(get_db)):
    funding = get_funding_by_id(db, funding_id)
    if not funding:
        raise HTTPException(status_code=404, detail="Funding opportunity not found")
    return funding