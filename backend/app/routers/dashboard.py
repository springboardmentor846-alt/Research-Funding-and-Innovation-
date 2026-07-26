from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.dependencies import get_current_user
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return aggregated stats for the Research Intelligence Dashboard:
    - Total publications, funding opportunities, open grants
    - Top research domains
    - Publication growth by year
    - Recent funding opportunities
    - Funding by agency (pie chart data)
    - Funding amount trend (area chart data)
    """
    return dashboard_service.get_dashboard_stats(db, current_user["id"])
