from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db

from app.utils.auth_dependency import (
    get_current_user
)

from app.services.dashboard_service import (
    get_dashboard_data
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/")
def dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_dashboard_data(
        db,
        current_user
    )