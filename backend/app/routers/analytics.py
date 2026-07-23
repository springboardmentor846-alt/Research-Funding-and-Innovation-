from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app import crud, schemas

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get(
    "/publication-trends",
    response_model=list[schemas.PublicationTrend]
)
def publication_trend(db: Session = Depends(get_db)):
    return crud.publication_trends(db)


@router.get(
    "/dashboard-summary",
    response_model=schemas.DashboardSummary
)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return crud.get_dashboard_summary(db, current_user)