from pydantic import BaseModel, Field


# ============================================================
# PATENT SEARCH
# ============================================================

class PatentSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    size: int = Field(default=10, ge=1, le=100)


class PatentResult(BaseModel):
    lens_id: str
    title: str
    applicant: str
    inventor: str
    publication_date: str
    jurisdiction: str
    legal_status: str


# ============================================================
# BOOKMARK
# ============================================================

class PatentBookmarkRequest(BaseModel):
    lens_id: str
    title: str
    applicant: str = ""
    jurisdiction: str = ""


# ============================================================
# SIMILAR PATENTS
# ============================================================

class SimilarPatentResult(BaseModel):
    lens_id: str
    title: str
    applicant: str
    publication_date: str
    jurisdiction: str


# ============================================================
# ANALYTICS
# ============================================================

class PatentAnalyticsRequest(BaseModel):
    query: str = Field(..., min_length=1)
    size: int = Field(default=100, ge=1, le=100)


# ============================================================
# COMPARISON
# ============================================================

class PatentComparisonRequest(BaseModel):
    lens_id_1: str
    lens_id_2: str


# ============================================================
# TIMELINE
# ============================================================

class PatentTimelineRequest(BaseModel):
    lens_id: str


# ============================================================
# AI INSIGHTS
# ============================================================

class PatentInsightRequest(BaseModel):
    lens_id: str