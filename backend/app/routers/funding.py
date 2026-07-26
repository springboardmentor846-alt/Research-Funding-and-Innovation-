from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.database.database import get_db
from app.auth.dependencies import get_current_user
from app.schemas.funding import FundingCreate, FundingResponse
from app.services import funding_service

router = APIRouter(prefix="/funding", tags=["Funding Opportunities"])


@router.get("/")
def list_funding(
    research_domain: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    agency: Optional[str] = Query(None),
    deadline_before: Optional[date] = Query(None),
    min_amount: Optional[float] = Query(None),
    max_amount: Optional[float] = Query(None),
    sort_by: Optional[str] = Query("latest"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all funding opportunities with optional filters and sorting."""
    return funding_service.get_all_funding(
        db, research_domain, country, agency,
        deadline_before, min_amount, max_amount,
        sort_by, skip, limit
    )


@router.get("/{funding_id}", response_model=FundingResponse)
def get_funding(
    funding_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a single funding opportunity by ID."""
    funding = funding_service.get_funding_by_id(db, funding_id)
    if not funding:
        raise HTTPException(status_code=404, detail="Funding opportunity not found")
    return funding


@router.post("/", response_model=FundingResponse, status_code=201)
def create_funding(
    funding: FundingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new funding opportunity. Admin and Innovation Manager only."""
    if current_user["role"] not in ("administrator", "innovation_manager"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return funding_service.create_funding(db, funding)


@router.put("/{funding_id}", response_model=FundingResponse)
def update_funding(
    funding_id: int,
    funding: FundingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a funding opportunity. Admin and Innovation Manager only."""
    if current_user["role"] not in ("administrator", "innovation_manager"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    updated = funding_service.update_funding(db, funding_id, funding)
    if not updated:
        raise HTTPException(status_code=404, detail="Funding opportunity not found")
    return updated


@router.delete("/{funding_id}")
def delete_funding(
    funding_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a funding opportunity. Admin only."""
    if current_user["role"] != "administrator":
        raise HTTPException(status_code=403, detail="Only administrators can delete funding")
    deleted = funding_service.delete_funding(db, funding_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Funding opportunity not found")
    return {"message": "Funding opportunity deleted successfully"}
