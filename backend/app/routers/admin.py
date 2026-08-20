from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.models.role import Role
from app.models.user import User


router = APIRouter(
    prefix="/admin",
    tags=["Administrator"],
)

ALLOWED_ROLES = {"researcher", "startup_founder", "administrator"}


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserRoleUpdate(BaseModel):
    role: str = Field(min_length=1, max_length=50)


def _role_name(db: Session, user: User) -> str:
    role = db.get(Role, user.role_id)
    return role.name if role else "unknown"


def _serialize_user(db: Session, user: User) -> dict:
    return {
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": _role_name(db, user),
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.get("/overview")
def admin_overview(
    current_user: User = Depends(require_role("administrator")),
    db: Session = Depends(get_db),
):
    total_users = db.scalar(select(func.count(User.id))) or 0
    active_users = db.scalar(
        select(func.count(User.id)).where(User.is_active.is_(True))
    ) or 0
    inactive_users = total_users - active_users

    role_counts = {}
    for role_name in ALLOWED_ROLES:
        role = db.scalar(select(Role).where(Role.name == role_name))
        if role is None:
            role_counts[role_name] = 0
            continue

        role_counts[role_name] = db.scalar(
            select(func.count(User.id)).where(User.role_id == role.id)
        ) or 0

    recent_users = db.scalars(
        select(User)
        .order_by(User.created_at.desc())
        .limit(8)
    ).all()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "researchers": role_counts.get("researcher", 0),
        "startup_founders": role_counts.get("startup_founder", 0),
        "administrators": role_counts.get("administrator", 0),
        "recent_users": [
            _serialize_user(db, user)
            for user in recent_users
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_admin": _serialize_user(db, current_user),
    }


@router.get("/users")
def list_users(
    search: str | None = Query(default=None, max_length=100),
    role: str | None = Query(default=None),
    status_filter: str = Query(default="all", alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(require_role("administrator")),
    db: Session = Depends(get_db),
):
    if role is not None and role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role filter.",
        )

    if status_filter not in {"all", "active", "inactive"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be all, active, or inactive.",
        )

    query = select(User)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.where(
            User.full_name.ilike(term)
            | User.email.ilike(term)
        )

    if role:
        role_record = db.scalar(
            select(Role).where(Role.name == role)
        )
        if role_record is None:
            return {
                "users": [],
                "page": page,
                "page_size": page_size,
                "total": 0,
                "total_pages": 0,
            }
        query = query.where(User.role_id == role_record.id)

    if status_filter == "active":
        query = query.where(User.is_active.is_(True))
    elif status_filter == "inactive":
        query = query.where(User.is_active.is_(False))

    count_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(count_query) or 0

    users = db.scalars(
        query
        .order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    total_pages = (total + page_size - 1) // page_size

    return {
        "users": [
            _serialize_user(db, user)
            for user in users
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
    }


@router.patch("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    current_user: User = Depends(require_role("administrator")),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if user.id == current_user.id and not payload.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own administrator account.",
        )

    target_role = _role_name(db, user)

    if (
        target_role == "administrator"
        and not payload.is_active
        and user.is_active
    ):
        active_admins = db.scalar(
            select(func.count(User.id))
            .join(Role, User.role_id == Role.id)
            .where(
                Role.name == "administrator",
                User.is_active.is_(True),
            )
        ) or 0

        if active_admins <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one active administrator account must remain.",
            )

    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)

    return {
        "message": (
            "User activated successfully."
            if user.is_active
            else "User deactivated successfully."
        ),
        "user": _serialize_user(db, user),
    }


@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    current_user: User = Depends(require_role("administrator")),
    db: Session = Depends(get_db),
):
    new_role_name = payload.role.strip().lower()

    if new_role_name not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Allowed roles: researcher, startup_founder, administrator.",
        )

    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    old_role_name = _role_name(db, user)

    if user.id == current_user.id and new_role_name != "administrator":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove administrator access from your own account.",
        )

    if (
        old_role_name == "administrator"
        and new_role_name != "administrator"
        and user.is_active
    ):
        active_admins = db.scalar(
            select(func.count(User.id))
            .join(Role, User.role_id == Role.id)
            .where(
                Role.name == "administrator",
                User.is_active.is_(True),
            )
        ) or 0

        if active_admins <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one active administrator account must remain.",
            )

    new_role = db.scalar(
        select(Role).where(Role.name == new_role_name)
    )

    if new_role is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The requested role is not configured in the database.",
        )

    user.role_id = new_role.id
    db.commit()
    db.refresh(user)

    return {
        "message": f"User role changed from {old_role_name} to {new_role_name}.",
        "user": _serialize_user(db, user),
    }
