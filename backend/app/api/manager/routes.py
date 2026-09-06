from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import require_role
from app.models.startup import Startup
from app.models.collaboration_request import CollaborationRequest
from app.services.dashboard_service import get_platform_overview

router = APIRouter()

# Innovation Manager gets platform-wide oversight, same as Admin,
# but through its own dashboard/routes rather than the Admin panel.
MANAGER_ROLES = ["innovation_manager", "admin"]


@router.get("/overview")
def manager_overview(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(MANAGER_ROLES)),
):
    """Innovation ecosystem overview: platform-wide numbers."""
    return get_platform_overview(db)


@router.get("/startups")
def manager_startups(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(MANAGER_ROLES)),
):
    """All startup profiles on the platform, for ecosystem oversight."""
    startups = db.query(Startup).all()
    return [
        {
            "id": s.id,
            "startup_name": s.startup_name,
            "industry": s.industry,
            "stage": s.stage,
            "funding_stage": s.funding_stage,
            "founder_email": s.user.email if s.user else None,
        }
        for s in startups
    ]


@router.get("/collaboration-activity")
def manager_collaboration_activity(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(MANAGER_ROLES)),
):
    """Recent collaboration requests across the platform, for oversight."""
    requests = (
        db.query(CollaborationRequest)
        .order_by(CollaborationRequest.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": r.id,
            "sender_email": r.sender.email if r.sender else None,
            "receiver_email": r.receiver.email if r.receiver else None,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in requests
    ]