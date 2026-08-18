"""Endpoints for researcher collaborations and funding-awarded history."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.research_domains import PREDEFINED_RESEARCH_DOMAINS
from app.schemas.profile import (
    CollaborationCreate,
    CollaborationUpdate,
    CollaborationResponse,
    CollaborationList,
    FundingHistoryCreate,
    FundingHistoryUpdate,
    FundingHistoryResponse,
    FundingHistoryList,
    ResearchInterestCreate,
    ResearchInterestUpdate,
    ResearchInterestResponse,
    ResearchInterestList,
    ResearchInterestReplaceAll,
    ResearchDomainCatalog,
)
from app.services.profile_service import CollaborationService, FundingHistoryService
from app.services.research_interest_service import ResearchInterestService
from app.services.recommendation_service import RecommendationService
from app.api.v1.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/profile", tags=["Profile"])


# ---------- Research Interests ----------
@router.get("/research-interests", response_model=ResearchInterestList)
def list_research_interests(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List the current user's research interests."""
    items = ResearchInterestService.list_for_user(db, current.id)
    return ResearchInterestList(items=items, total=len(items))


@router.post(
    "/research-interests",
    response_model=ResearchInterestResponse,
    status_code=201,
)
def create_research_interest(
    payload: ResearchInterestCreate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a single research interest (predefined or custom)."""
    out = ResearchInterestService.add(
        db, current, payload.name, is_custom=payload.is_custom
    )
    # The user's research profile changed — drop the cached recommendations
    # so the next read recomputes.
    RecommendationService.invalidate_for_user(db, current.id)
    return out


@router.put(
    "/research-interests/{interest_id}",
    response_model=ResearchInterestResponse,
)
def update_research_interest(
    interest_id: int,
    payload: ResearchInterestUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Rename a research interest."""
    out = ResearchInterestService.update(db, current, interest_id, payload.name)
    RecommendationService.invalidate_for_user(db, current.id)
    return out


@router.delete("/research-interests/{interest_id}", status_code=204)
def delete_research_interest(
    interest_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a research interest."""
    ResearchInterestService.delete(db, current, interest_id)
    RecommendationService.invalidate_for_user(db, current.id)
    return None


@router.put(
    "/research-interests",
    response_model=ResearchInterestList,
)
def replace_research_interests(
    payload: ResearchInterestReplaceAll,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bulk replace the user's full interest set in one call."""
    items = ResearchInterestService.replace_all(db, current, payload.items)
    RecommendationService.invalidate_for_user(db, current.id)
    return ResearchInterestList(items=items, total=len(items))


@router.get("/research-domains", response_model=ResearchDomainCatalog)
def list_research_domains(
    _current: User = Depends(get_current_user),
):
    """Return the predefined research domain catalog."""
    return ResearchDomainCatalog(domains=list(PREDEFINED_RESEARCH_DOMAINS))


# ---------- Collaborations ----------
@router.get("/collaborations", response_model=CollaborationList)
def list_collaborations(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = CollaborationService.list_for_user(db, current.id)
    return CollaborationList(items=items, total=len(items))


@router.post("/collaborations", response_model=CollaborationResponse, status_code=201)
def create_collaboration(
    payload: CollaborationCreate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CollaborationService.create(db, current.id, payload)


@router.put("/collaborations/{collab_id}", response_model=CollaborationResponse)
def update_collaboration(
    collab_id: int,
    payload: CollaborationUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    collab = CollaborationService.get_by_id(db, collab_id, current.id)
    if not collab:
        raise HTTPException(status_code=404, detail="Collaboration not found")
    return CollaborationService.update(db, collab, payload)


@router.delete("/collaborations/{collab_id}")
def delete_collaboration(
    collab_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    collab = CollaborationService.get_by_id(db, collab_id, current.id)
    if not collab:
        raise HTTPException(status_code=404, detail="Collaboration not found")
    CollaborationService.delete(db, collab)
    return {"message": "Collaboration deleted"}


# ---------- Funding History ----------
@router.get("/funding-history", response_model=FundingHistoryList)
def list_funding_history(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = FundingHistoryService.list_for_user(db, current.id)
    total_amount = sum((r.amount or 0) for r in items if r.status in ("awarded", "completed"))
    return FundingHistoryList(items=items, total=len(items), total_amount=total_amount)


@router.post("/funding-history", response_model=FundingHistoryResponse, status_code=201)
def create_funding_history(
    payload: FundingHistoryCreate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return FundingHistoryService.create(db, current.id, payload)


@router.put("/funding-history/{hist_id}", response_model=FundingHistoryResponse)
def update_funding_history(
    hist_id: int,
    payload: FundingHistoryUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = FundingHistoryService.get_by_id(db, hist_id, current.id)
    if not record:
        raise HTTPException(status_code=404, detail="Funding record not found")
    return FundingHistoryService.update(db, record, payload)


@router.delete("/funding-history/{hist_id}")
def delete_funding_history(
    hist_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = FundingHistoryService.get_by_id(db, hist_id, current.id)
    if not record:
        raise HTTPException(status_code=404, detail="Funding record not found")
    FundingHistoryService.delete(db, record)
    return {"message": "Funding record deleted"}
