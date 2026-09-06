from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user, require_role
from app.crud.user import get_user_by_email
from app.services.dashboard_service import get_user_dashboard, get_platform_overview

router = APIRouter()


@router.get("/overview")
def my_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Aggregated activity snapshot for the logged-in user."""
    user = get_user_by_email(db, current_user.get("sub"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return get_user_dashboard(db, user.id)


@router.get("/platform")
def platform_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["admin", "innovation_manager"])),
):
    """Platform-wide stats for Admin / Innovation Manager dashboards."""
    return get_platform_overview(db)