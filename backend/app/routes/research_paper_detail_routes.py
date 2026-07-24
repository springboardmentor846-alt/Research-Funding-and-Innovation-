from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.utils.auth_dependency import get_current_user

from app.schemas.research_paper_detail_schema import (
    ResearchPaperDetailCreate,
    ResearchPaperDetailUpdate,
    ResearchPaperDetailResponse,
)

from app.services.research_paper_detail_service import (
    ResearchPaperDetailService,
)

router = APIRouter(
    prefix="/research-paper-details",
    tags=["Research Paper Details"]
)


@router.post(
    "/{portfolio_id}",
    response_model=ResearchPaperDetailResponse
)
def create_research_paper_detail(
    portfolio_id: int,
    research_paper: ResearchPaperDetailCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return ResearchPaperDetailService.create_research_paper_detail(
        db,
        portfolio_id,
        research_paper,
        current_user
    )


@router.get(
    "/{portfolio_id}",
    response_model=ResearchPaperDetailResponse
)
def get_research_paper_detail(
    portfolio_id: int,
    db: Session = Depends(get_db)
):
    return ResearchPaperDetailService.get_research_paper_detail(
        db,
        portfolio_id
    )


@router.put(
    "/{portfolio_id}",
    response_model=ResearchPaperDetailResponse
)
def update_research_paper_detail(
    portfolio_id: int,
    research_paper: ResearchPaperDetailUpdate,
    db: Session = Depends(get_db)
):
    return ResearchPaperDetailService.update_research_paper_detail(
        db,
        portfolio_id,
        research_paper
    )


@router.delete("/{portfolio_id}")
def delete_research_paper_detail(
    portfolio_id: int,
    db: Session = Depends(get_db)
):
    return ResearchPaperDetailService.delete_research_paper_detail(
        db,
        portfolio_id
    )