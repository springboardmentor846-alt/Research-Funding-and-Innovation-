from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth_deps import require_role
from app.models.models import User, AuditLog
from app.schemas.schemas import UserRead
from typing import List

router = APIRouter(prefix="/admin", tags=["Admin Panel"])

@router.get("/users", response_model=List[UserRead])
def admin_list_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(["Administrator"]))
):
    return db.query(User).all()

@router.put("/users/{user_id}/status")
def admin_toggle_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(["Administrator"]))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.is_active = is_active
    db.commit()
    return {"message": f"User status set to {'active' if is_active else 'inactive'}."}

@router.get("/audit-logs")
def admin_list_audit_logs(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(["Administrator"]))
):
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()

@router.post("/seed-database")
def admin_seed_database(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(["Administrator"]))
):
    from app.utils.seed_data import seed_all_sample_data
    result = seed_all_sample_data(db, force=True)
    return result
