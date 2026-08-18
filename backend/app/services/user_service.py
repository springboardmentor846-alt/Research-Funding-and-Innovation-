"""User service: business logic for user operations."""
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException, status
from typing import Optional

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password
from app.core.logging import logger
from app.services.recommendation_service import RecommendationService


# Fields on the User row that contribute to the recommendation signal.
# Editing any of these invalidates the user's cached recommendations.
_RELEVANT_USER_FIELDS = frozenset(
    {"research_interests", "skills", "bio", "affiliation"}
)


class UserService:
    """Service class for user operations."""

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def create_user(db: Session, payload: UserCreate) -> User:
        """Create a new user with hashed password."""
        if UserService.get_by_email(db, payload.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        if UserService.get_by_username(db, payload.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

        user = User(
            email=payload.email,
            username=payload.username,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
            role=payload.role,
            affiliation=payload.affiliation,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created user: {user.username} (role={user.role})")
        return user

    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate by username or email + password."""
        user = db.query(User).filter(
            or_(User.username == username, User.email == username)
        ).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    @staticmethod
    def update_user(db: Session, user: User, payload: UserUpdate) -> User:
        """Update a user profile."""
        update_data = payload.model_dump(exclude_unset=True)
        # Capture the set of scoring-relevant fields the caller is about
        # to change so we can invalidate the cache only when needed.
        touched = set(update_data.keys()) & _RELEVANT_USER_FIELDS
        for field, value in update_data.items():
            setattr(user, field, value)
        db.commit()
        db.refresh(user)
        if touched:
            RecommendationService.invalidate_for_user(db, user.id)
        return user

    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 50) -> list[User]:
        return db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def list_users_paginated(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[list[User], int]:
        """Admin paginated + filtered list of users."""
        query = db.query(User)
        if search:
            term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(User.username).like(term),
                    func.lower(User.email).like(term),
                    func.lower(func.coalesce(User.full_name, "")).like(term),
                )
            )
        if role is not None:
            query = query.filter(User.role == role)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        total = query.count()
        items = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def admin_stats(db: Session) -> dict:
        """Aggregate user statistics for the admin dashboard."""
        total = db.query(func.count(User.id)).scalar() or 0
        active = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
        inactive = total - active
        verified = db.query(func.count(User.id)).filter(User.is_verified == True).scalar() or 0
        by_role_rows = (
            db.query(User.role, func.count(User.id))
            .group_by(User.role)
            .all()
        )
        by_role = {r.value: cnt for (r, cnt) in by_role_rows}
        # Active in last 30 days
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(days=30)
        active_30d = (
            db.query(func.count(User.id))
            .filter(User.last_login != None, User.last_login >= cutoff)  # noqa: E711
            .scalar()
            or 0
        )
        return {
            "total_users": int(total),
            "active_users": int(active),
            "inactive_users": int(inactive),
            "verified_users": int(verified),
            "by_role": by_role,
            "active_30d": int(active_30d),
        }

    @staticmethod
    def change_role(db: Session, user_id: int, role: UserRole) -> User:
        """DEPRECATED: role mutation has been removed for security.
        This method is kept for internal seed/admin tooling only and should
        not be exposed via the HTTP API.
        """
        user = UserService.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.role = role
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> User:
        user = UserService.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user_permanent(db: Session, user_id: int) -> None:
        """Hard delete a user and their owned data (cascade via relationships)."""
        user = UserService.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        try:
            db.delete(user)
            db.commit()
            logger.warning(f"User {user.username} (id={user.id}) permanently deleted")
        except Exception as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to delete user: {exc}",
            )
