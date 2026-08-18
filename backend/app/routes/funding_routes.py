from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db

from app.schemas.funding_schema import (
    FundingSearchRequest,
    FundingDetailRequest,
    FundingBookmarkRequest,
     FundingAnalyticsRequest,
     FundingAIInsightRequest,
     FundingProposalRequest,
     FundingRecommendationRequest,
     FundingDeadlineRequest

)

from app.services.funding_service import (
    search_funding,
    get_funding_details,
    save_funding_bookmark,
     get_funding_bookmarks,
     delete_funding_bookmark,
     get_funding_analytics,
     get_funding_ai_insights,
     generate_funding_proposal,
     get_funding_recommendations,
     get_funding_deadlines
)

from app.utils.auth_dependency import get_current_user


router = APIRouter(
    prefix="/funding",
    tags=["Funding Intelligence"]
)


@router.post("/search")
def funding_search(
    request: FundingSearchRequest
):
    return search_funding(
        request.keyword
    )


@router.post("/details")
def funding_details(
    request: FundingDetailRequest
):
    return get_funding_details(
        request.opportunity_id
    )


@router.post("/bookmark")
def bookmark_funding(
    bookmark: FundingBookmarkRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return save_funding_bookmark(
        db,
        current_user["id"],
        bookmark
    )
@router.get("/bookmarks")
def my_funding_bookmarks(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_funding_bookmarks(
        db,
        current_user["id"]
    )
@router.delete("/bookmark/{bookmark_id}")
def remove_funding_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return delete_funding_bookmark(
        db,
        bookmark_id,
        current_user["id"]
    )
@router.post("/analytics")
def funding_analytics(
    request: FundingAnalyticsRequest
):
    return get_funding_analytics(
        request.keyword,
        request.size
    )
@router.post("/ai-insights")
def funding_ai_insights(
    request: FundingAIInsightRequest
):
    return get_funding_ai_insights(
        request.opportunity_id
    )
@router.post("/generate-proposal")
def funding_proposal(
    request: FundingProposalRequest
):
    return generate_funding_proposal(
        request.opportunity_id,
        request.project_title,
        request.project_description,
        request.organization_name
    )
@router.post("/recommendations")
def funding_recommendations(
    request: FundingRecommendationRequest
):
    return get_funding_recommendations(
        request.project_title,
        request.project_description,
        request.keyword,
        request.size
    )
@router.post("/deadlines")
def funding_deadlines(
    request: FundingDeadlineRequest
):
    return get_funding_deadlines(
        request.keyword,
        request.size
    )