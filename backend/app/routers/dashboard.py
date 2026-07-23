from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app import schemas, crud

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "/summary",
    response_model=schemas.DashboardSummary
)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return crud.get_dashboard_summary(db, current_user)


@router.get("/publication-trends")
def publication_trends(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return crud.publication_trends(db, current_user)
