from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db

from app.schemas.patent_schema import (
    PatentSearchRequest,
    PatentBookmarkRequest,
    PatentAnalyticsRequest,
    PatentComparisonRequest,
    PatentInsightRequest,
)

from app.services.patent_service import (
    search_patents,
    format_patents,
    get_patent_details,
    get_similar_patents,
    save_bookmark,
    get_bookmarks,
    delete_bookmark,
    get_patent_analytics,
    compare_patents,
    get_patent_timeline,
    get_patent_ai_insights,
)

from app.utils.auth_dependency import get_current_user


router = APIRouter(
    prefix="/patents",
    tags=["Patent Intelligence"],
)


# ============================================================
# SEARCH
# ============================================================

@router.post("/search")
def patent_search(
    request: PatentSearchRequest
):

    response = search_patents(
        request.query,
        request.size
    )

    results = response.get(
        "data",
        []
    )

    formatted_results = format_patents(
        results
    )

    return {
        "count":
            len(formatted_results),

        "results":
            formatted_results,

        "source":
            "mock"
            if response.get("mock")
            else "lens"
    }


# ============================================================
# BOOKMARK
# ============================================================

@router.post("/bookmark")
def bookmark_patent(
    bookmark: PatentBookmarkRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return save_bookmark(
        db,
        current_user["id"],
        bookmark
    )


# ============================================================
# MY BOOKMARKS
# ============================================================

@router.get("/bookmarks")
def my_bookmarks(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return get_bookmarks(
        db,
        current_user["id"]
    )


# ============================================================
# DELETE BOOKMARK
# ============================================================

@router.delete(
    "/bookmark/{bookmark_id}"
)
def remove_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return delete_bookmark(
        db,
        bookmark_id,
        current_user["id"]
    )


# ============================================================
# ANALYTICS
# ============================================================

@router.post("/analytics")
def patent_analytics(
    request: PatentAnalyticsRequest
):

    return get_patent_analytics(
        request.query,
        request.size
    )


# ============================================================
# COMPARISON
# ============================================================

@router.post("/compare")
def patent_comparison(
    request: PatentComparisonRequest
):

    return compare_patents(
        request.lens_id_1,
        request.lens_id_2
    )


# ============================================================
# AI INSIGHTS
# ============================================================

@router.post("/ai-insights")
def patent_ai_insights(
    request: PatentInsightRequest
):

    return get_patent_ai_insights(
        request.lens_id
    )


# ============================================================
# SIMILAR PATENTS
# ============================================================

@router.get(
    "/{lens_id}/similar"
)
def similar_patents(
    lens_id: str
):

    results = get_similar_patents(
        lens_id
    )

    return {
        "count":
            len(results),

        "results":
            results
    }


# ============================================================
# TIMELINE
# ============================================================

@router.get(
    "/{lens_id}/timeline"
)
def patent_timeline(
    lens_id: str
):

    return get_patent_timeline(
        lens_id
    )


# ============================================================
# DETAILS
# ============================================================

@router.get(
    "/{lens_id}"
)
def patent_details(
    lens_id: str
):

    return get_patent_details(
        lens_id
    )