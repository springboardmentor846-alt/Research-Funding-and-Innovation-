"""Saved Patents REST endpoints (user-scoped).

Mounted at ``/api/v1/saved-patents`` from ``app.main``.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.db import get_db
from app.models.saved_patent import SavedPatent
from app.models.user import User
from app.schemas.saved_patent import (
    SavedPatentCountResponse,
    SavedPatentCreate,
    SavedPatentListResponse,
    SavedPatentResponse,
)
from app.services.saved_patent_service import SavedPatentService

router = APIRouter(prefix="/saved-patents", tags=["Saved Patents"])


@router.post(
    "",
    response_model=SavedPatentResponse,
    status_code=201,
    summary="Bookmark a patent (idempotent)",
)
def save_patent(
    payload: SavedPatentCreate,
    response: Response,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bookmark a patent for the current user.

    Returns the existing row with ``200 OK`` if the patent is already
    saved (idempotent), or creates a new row with ``201 Created`` on
    the first save.
    """
    existing = SavedPatentService.find_existing(
        db, current.id, payload.patent_number, payload.source
    )
    if existing is not None:
        response.status_code = 200
        return existing
    return SavedPatentService.create(db, current.id, payload)


@router.get(
    "",
    response_model=SavedPatentListResponse,
    summary="List saved patents for the current user",
)
def list_saved_patents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    sort_by: str = Query(
        "saved_at",
        pattern="^(saved_at|publication_date|publication_year|title|citation_count)$",
    ),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Paginated, searchable, filterable, sortable saved-patent list.

    ``sort_by`` and ``sort_order`` are constrained to a fixed whitelist
    so SQL injection via these parameters is impossible.
    """
    skip = (page - 1) * page_size
    items, total, sources = SavedPatentService.list_for_user(
        db,
        current.id,
        skip=skip,
        limit=page_size,
        search=search,
        source=source,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    total_pages = (total + page_size - 1) // page_size if total else 0
    return SavedPatentListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        sources=sources,
    )


@router.get(
    "/count",
    response_model=SavedPatentCountResponse,
    summary="Saved-patent count for the current user",
)
def saved_patent_count(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return ``{"count": N}`` for the current user.

    Used by the Dashboard KPI tile.
    """
    return SavedPatentCountResponse(
        count=SavedPatentService.count_for_user(db, current.id)
    )


@router.get(
    "/{saved_id}",
    response_model=SavedPatentResponse,
    summary="Get a saved patent by id",
)
def get_saved_patent(
    saved_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = SavedPatentService.get_by_id(db, saved_id, current.id)
    if row is None:
        # Distinguish "doesn't exist" from "belongs to someone else" so
        # we can honestly answer 403 vs 404 without leaking the row's
        # existence to non-owners.
        any_owner = (
            db.query(SavedPatent)
            .filter(SavedPatent.id == saved_id)
            .one_or_none()
        )
        if any_owner is not None:
            raise HTTPException(
                status_code=403, detail="Not authorized"
            )
        raise HTTPException(
            status_code=404, detail="Saved patent not found"
        )
    return row


@router.delete(
    "/{saved_id}",
    summary="Remove a saved patent",
)
def delete_saved_patent(
    saved_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = SavedPatentService.get_by_id(db, saved_id, current.id)
    if row is None:
        any_owner = (
            db.query(SavedPatent)
            .filter(SavedPatent.id == saved_id)
            .one_or_none()
        )
        if any_owner is not None:
            raise HTTPException(
                status_code=403, detail="Not authorized"
            )
        raise HTTPException(
            status_code=404, detail="Saved patent not found"
        )
    SavedPatentService.delete(db, row)
    return {"message": "Saved patent removed", "id": saved_id}