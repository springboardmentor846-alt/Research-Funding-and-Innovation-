from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app import crud, schemas

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


# ==========================
# Publication Analytics
# ==========================

@router.get(
    "/publication-trends",
    response_model=list[schemas.PublicationTrend]
)
def publication_trend(db: Session = Depends(get_db)):
    return crud.publication_trends(db)


# ==========================
# Dashboard Summary
# ==========================

@router.get(
    "/dashboard-summary",
    response_model=schemas.DashboardSummary
)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return crud.get_dashboard_summary(db, current_user)


# ==========================
# Patent Analytics (Milestone 3)
# ==========================

@router.get(
    "/patent-trends",
    response_model=list[schemas.PatentTrendResponse]
)
def patent_trends(
    db: Session = Depends(get_db)
):
    return crud.patent_trends(db)


@router.get(
    "/technology-domains",
    response_model=list[schemas.TechnologyDomainResponse]
)
def technology_domains(
    db: Session = Depends(get_db)
):
    return crud.technology_domain_analysis(db)


@router.get(
    "/top-assignees",
    response_model=list[schemas.TopAssigneeResponse]
)
def top_assignees(
    db: Session = Depends(get_db)
):
    return crud.top_assignees(db)


@router.get(
    "/innovation-score",
    response_model=schemas.InnovationScoreResponse
)
def innovation_score(
    db: Session = Depends(get_db)
):
    return crud.innovation_score(db)