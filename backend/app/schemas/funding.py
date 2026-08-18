"""Funding-related Pydantic schemas."""
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Any, Optional, List
from datetime import datetime


_SUMMARY_MAX = 280


def _build_summary(row: Any) -> str:
    """Pick the best short description available on a row.

    Used for the ``summary`` field returned by the API and the recommender.
    Priority: explicit ``summary`` column → trimmed ``description`` → title.
    """
    explicit = getattr(row, "summary", None)
    if explicit:
        return explicit
    desc = (getattr(row, "description", None) or "").strip()
    if not desc:
        return (getattr(row, "title", "") or "")[:_SUMMARY_MAX]
    if len(desc) > _SUMMARY_MAX:
        return desc[: _SUMMARY_MAX - 1].rstrip() + "…"
    return desc


def _primary_topic(row: Any) -> str:
    for value in (
        getattr(row, "research_area", None),
        getattr(row, "category", None),
        getattr(row, "research_domain", None),
    ):
        if value:
            return value
    return ""


_SOURCE_LABELS = {
    "nih": "NIH RePORTER",
    "nsf": "NSF Awards",
    "grants_gov": "Grants.gov",
    "openalex": "OpenAlex",
    "cordis": "CORDIS (EU)",
    "admin": "Administrator",
}


def _source_label(source: Optional[str]) -> str:
    return _SOURCE_LABELS.get(source or "", "")


class FundingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    keywords: Optional[str] = None
    research_domain: Optional[str] = None
    research_area: Optional[str] = None
    category: Optional[str] = None
    agency: Optional[str] = None
    organization: Optional[str] = None
    sponsor: Optional[str] = None
    country: Optional[str] = None
    funding_type: Optional[str] = None
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    currency: str = "USD"
    application_deadline: Optional[datetime] = None
    posted_date: Optional[datetime] = None
    status: Optional[str] = None
    eligibility: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None


class FundingCreate(FundingBase):
    pass


class FundingUpdate(BaseModel):
    """Partial update payload for a funding opportunity. All fields optional."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, min_length=1)
    keywords: Optional[str] = None
    research_domain: Optional[str] = None
    research_area: Optional[str] = None
    category: Optional[str] = None
    agency: Optional[str] = None
    organization: Optional[str] = None
    sponsor: Optional[str] = None
    country: Optional[str] = None
    funding_type: Optional[str] = None
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    currency: Optional[str] = None
    application_deadline: Optional[datetime] = None
    posted_date: Optional[datetime] = None
    status: Optional[str] = None
    eligibility: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    is_active: Optional[bool] = None


class FundingResponse(FundingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    summary: str = ""
    primary_topic: str = ""
    source_label: str = ""

    @model_validator(mode="before")
    @classmethod
    def _populate_computed(cls, data: Any) -> Any:
        """When validating from an ORM row, fill the computed fields."""
        if hasattr(data, "__table__") or hasattr(data, "_sa_instance_state"):
            return {
                **(data.__dict__ if hasattr(data, "__dict__") else {}),
                "summary": _build_summary(data),
                "primary_topic": _primary_topic(data),
                "source_label": _source_label(getattr(data, "source", None)),
            }
        return data


class FundingList(BaseModel):
    items: List[FundingResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class RecommendationItem(BaseModel):
    """A single funding recommendation."""
    funding: FundingResponse
    similarity_score: float
    matching_percentage: float
    matching_keywords: List[str]
    explanation: str
    rule_score: float
    # Score breakdown — populated by the new weighted recommender. Defaults
    # keep older callers working unchanged.
    interest_score: float = 0.0
    keyword_score: float = 0.0
    eligibility_score: float = 0.0
    history_penalty_applied: bool = False


class RecommendationResponse(BaseModel):
    """Response containing a list of recommendations."""
    user_id: int
    recommendations: List[RecommendationItem]
    total: int
    generated_at: datetime
    cache_hit: bool = False
