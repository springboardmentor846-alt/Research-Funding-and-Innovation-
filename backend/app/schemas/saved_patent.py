"""Pydantic v2 schemas for the Saved Patents feature.

Mirrors the style of ``schemas/publication.py`` and ``schemas/patent.py``.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SavedPatentBase(BaseModel):
    patent_number: str = Field(..., min_length=1, max_length=64)
    title: str = Field(..., min_length=1, max_length=1024)
    source: str = Field(..., min_length=1, max_length=32)
    inventors: Optional[str] = None
    assignee: Optional[str] = None
    technology_area: Optional[str] = None
    publication_date: Optional[datetime] = None
    publication_year: Optional[int] = None
    citation_count: int = 0
    url: Optional[str] = None
    lens_url: Optional[str] = None
    abstract: Optional[str] = None


class SavedPatentCreate(SavedPatentBase):
    """Request body for ``POST /saved-patents``.

    All optional fields are denormalised from the original patent record;
    only ``patent_number``, ``source`` and ``title`` are required.
    """

    pass


class SavedPatentUpdate(BaseModel):
    """Placeholder — saved patents are snapshots, not editable."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=1024)


class SavedPatentResponse(SavedPatentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    saved_at: datetime
    updated_at: datetime


class SavedPatentListResponse(BaseModel):
    """Paginated response shape used by ``GET /saved-patents``."""

    items: List[SavedPatentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    sources: Optional[List[str]] = None


class SavedPatentCountResponse(BaseModel):
    count: int