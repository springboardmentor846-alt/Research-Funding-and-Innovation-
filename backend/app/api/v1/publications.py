"""Publication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db import get_db
from app.schemas.publication import (
    PublicationCreate,
    PublicationUpdate,
    PublicationResponse,
    PublicationList,
)
from app.services.publication_service import PublicationService
from app.api.v1.deps import get_current_user
from app.models.user import User, UserRole
from app.api.v1.deps import require_role

router = APIRouter(prefix="/publications", tags=["Publications"])


@router.post("", response_model=PublicationResponse, status_code=201)
def create_publication(
    payload: PublicationCreate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a new publication to the current user's library.

    A new publication changes the user's research profile, so the
    cached recommendations are dropped: the next ``/recommendations/me``
    read will recompute with the expanded profile.
    """
    out = PublicationService.create(db, current.id, payload)
    from app.services.recommendation_service import RecommendationService
    RecommendationService.invalidate_for_user(db, current.id)
    return out


@router.get("", response_model=PublicationList)
def list_publications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    domain: Optional[str] = None,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List publications owned by the current user."""
    skip = (page - 1) * page_size
    items, total = PublicationService.list_for_user(
        db, current.id, skip=skip, limit=page_size, search=search, domain=domain
    )
    total_pages = (total + page_size - 1) // page_size if total else 0
    return PublicationList(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)


@router.get("/all", response_model=PublicationList)
def list_all_publications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    domain: Optional[str] = None,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all publications on the platform."""
    skip = (page - 1) * page_size
    items, total = PublicationService.list_all(
        db, skip=skip, limit=page_size, search=search, domain=domain
    )
    total_pages = (total + page_size - 1) // page_size if total else 0
    return PublicationList(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)


@router.get("/admin/all", response_model=PublicationList)
def admin_list_publications(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    domain: Optional[str] = None,
    owner_id: Optional[int] = None,
    _admin: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Admin-only: list publications across all researchers with filters & pagination."""
    skip = (page - 1) * page_size
    items, total = PublicationService.list_all_for_admin(
        db, skip=skip, limit=page_size, search=search, domain=domain, owner_id=owner_id
    )
    total_pages = (total + page_size - 1) // page_size if total else 0
    return PublicationList(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)


@router.get("/{pub_id}", response_model=PublicationResponse)
def get_publication(
    pub_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pub = PublicationService.get_by_id(db, pub_id)
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")
    if pub.owner_id != current.id and current.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to view this publication")
    return pub


@router.put("/{pub_id}", response_model=PublicationResponse)
def update_publication(
    pub_id: int,
    payload: PublicationUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pub = PublicationService.get_by_id(db, pub_id)
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")
    if pub.owner_id != current.id and current.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    out = PublicationService.update(db, pub, payload)
    from app.services.recommendation_service import RecommendationService
    RecommendationService.invalidate_for_user(db, current.id)
    return out


@router.delete("/{pub_id}")
def delete_publication(
    pub_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pub = PublicationService.get_by_id(db, pub_id)
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")
    if pub.owner_id != current.id and current.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    PublicationService.delete(db, pub)
    from app.services.recommendation_service import RecommendationService
    RecommendationService.invalidate_for_user(db, current.id)
    return {"message": "Publication deleted"}


@router.get("/stats/me")
def my_publication_stats(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return aggregate stats for the current user's publications."""
    return PublicationService.get_stats(db, current.id)
