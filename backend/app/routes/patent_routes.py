from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db

from app.schemas.patent_schema import PatentSearchRequest

from app.schemas.patent_schema import PatentBookmarkRequest
from app.schemas.patent_schema import PatentAnalyticsRequest
from app.schemas.patent_schema import PatentComparisonRequest
from app.schemas.patent_schema import PatentTimelineRequest
from app.schemas.patent_schema import PatentInsightRequest
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
    get_patent_ai_insights
)
from app.utils.auth_dependency import get_current_user

router = APIRouter(
    prefix="/patents",
    tags=["Patent Intelligence"]
)


@router.post("/search")
def patent_search(request: PatentSearchRequest):

    # Call Lens API
    response = search_patents(
        request.query,
        request.size
    )

    # Extract patent list
    results = response.get("data", [])

    # Format patent data
    formatted_results = format_patents(results)

    # Return clean response
    return {
        "count": len(formatted_results),
        "results": formatted_results
    }
@router.get("/{lens_id}/similar")
def similar_patents(lens_id: str):

    results = get_similar_patents(lens_id)

    return {
        "count": len(results),
        "results": results
    }
@router.get("/{lens_id}")
def patent_details(lens_id: str):

    result = get_patent_details(lens_id)

    return result
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
@router.get("/bookmarks")
def my_bookmarks(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_bookmarks(
        db,
        current_user["id"]
    )
@router.delete("/bookmark/{bookmark_id}")
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
@router.post("/analytics")
def patent_analytics(
    request: PatentAnalyticsRequest
):
    return get_patent_analytics(
        request.query,
        request.size
    )
@router.post("/compare")
def patent_comparison(
    request: PatentComparisonRequest
):
    return compare_patents(
        request.lens_id_1,
        request.lens_id_2
    )
@router.get("/{lens_id}/timeline")
def patent_timeline(
    lens_id: str
):
    return get_patent_timeline(lens_id)
@router.post("/ai-insights")
def patent_ai_insights(
    request: PatentInsightRequest
):
    return get_patent_ai_insights(
        request.lens_id
    )