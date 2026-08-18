"""Authentication & user endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db import get_db
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    UserStats,
    Token,
    TokenRefresh,
)
from app.services.user_service import UserService
from app.services.publication_service import PublicationService
from app.services.profile_service import FundingHistoryService
from app.services.research_interest_service import ResearchInterestService
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
    hash_password,
)
from app.core.config import settings
from app.core.logging import logger
from app.api.v1.deps import get_current_user, require_role
from app.models.user import User, UserRole

router = APIRouter(prefix="/auth", tags=["Authentication"])


class AdminUserUpdate(BaseModel):
    """Admin-only safe user profile update payload (no role change)."""
    full_name: Optional[str] = None
    affiliation: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class ChangePasswordPayload(BaseModel):
    old_password: str
    new_password: str


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    user = UserService.create_user(db, payload)
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with username/email and password. Returns access + refresh tokens."""
    user = UserService.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    user.last_login = datetime.utcnow()
    db.commit()
    access = create_access_token(subject=user.id)
    refresh = create_refresh_token(subject=user.id)
    return Token(access_token=access, refresh_token=refresh)


@router.post("/login/json", response_model=Token)
def login_json(payload: UserLogin, db: Session = Depends(get_db)):
    """JSON-style login (for SPA clients)."""
    user = UserService.authenticate(db, payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user.last_login = datetime.utcnow()
    db.commit()
    return Token(
        access_token=create_access_token(subject=user.id),
        refresh_token=create_refresh_token(subject=user.id),
    )


@router.post("/refresh", response_model=Token)
def refresh_token(payload: TokenRefresh, db: Session = Depends(get_db)):
    """Exchange a refresh token for a new token pair."""
    data = decode_token(payload.refresh_token)
    if not data or data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user_id = data.get("sub")
    user = UserService.get_by_id(db, int(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not active")
    return Token(
        access_token=create_access_token(subject=user.id),
        refresh_token=create_refresh_token(subject=user.id),
    )


@router.post("/logout")
def logout(current: User = Depends(get_current_user)):
    """Logout endpoint. JWTs are stateless; client should drop the token."""
    logger.info(f"User {current.username} logged out")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def read_me(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return the currently-authenticated user."""
    interests = ResearchInterestService.list_for_user(db, current.id)
    return UserResponse.model_validate({**current.__dict__, "interests": interests})


@router.put("/me", response_model=UserResponse)
def update_me(payload: UserUpdate, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update the current user's profile.

    Backward compatibility: if `research_interests` (the legacy CSV string)
    is provided, it replaces the structured interest set. The structured set
    remains the source of truth — the CSV column is mirrored back from it.

    Any profile change (interests, bio, affiliation, country) invalidates
    the cached recommendations so the next read recomputes against the
    fresh profile.
    """
    raw = payload.research_interests
    update = UserUpdate(**{**payload.model_dump(exclude_unset=True), "research_interests": None})
    user = UserService.update_user(db, current, update)
    interests_changed = False
    if raw is not None:
        names = [n.strip() for n in raw.split(",") if n.strip()]
        ResearchInterestService.replace_all(db, user, names)
        interests_changed = True
    db.refresh(user)
    if interests_changed:
        from app.services.recommendation_service import RecommendationService
        RecommendationService.invalidate_for_user(db, user.id)
    interests = ResearchInterestService.list_for_user(db, user.id)
    return UserResponse.model_validate({**user.__dict__, "interests": interests})


@router.get("/me/stats", response_model=UserStats)
def my_stats(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return profile statistics for the current user."""
    pub_stats = PublicationService.get_stats(db, current.id)
    funding_stats = FundingHistoryService.stats(db, current.id)
    return UserStats(
        total_publications=pub_stats["total_publications"],
        total_citations=pub_stats["total_citations"],
        h_index=current.h_index,
        i10_index=current.i10_index,
        recommendations_count=len(current.recommendations),
        funding_awarded=funding_stats["total_awards"],
        funding_awarded_amount=funding_stats["total_amount"],
        collaborations_count=len(current.collaborations),
    )


@router.post("/change-password")
def change_password(
    payload: ChangePasswordPayload,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change the current user's password."""
    if not verify_password(payload.old_password, current.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    if len(payload.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    current.hashed_password = hash_password(payload.new_password)
    db.commit()
    return {"message": "Password changed"}


# Admin endpoints
# NOTE: Users select their own role at registration. The admin can manage
# accounts (deactivate / activate / delete / edit profile fields) but MUST NOT
# assign or change roles. This is enforced by the explicit allowlist below and
# the lack of any role-mutation endpoint.
@router.get("/users", response_model=list[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role(UserRole.ADMIN)),
):
    """List all users (admin only). Read-only listing; no role mutation."""
    return UserService.list_users(db, skip=skip, limit=limit)


@router.put("/users/{user_id}", response_model=UserResponse)
def admin_update_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role(UserRole.ADMIN)),
):
    """Admin update of safe profile fields (name, affiliation, active/verified)."""
    user = UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        # Hard guard: admin must not change role
        if field == "role":
            continue
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/activate", response_model=UserResponse)
def admin_activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role(UserRole.ADMIN)),
):
    """Reactivate a deactivated user (admin only)."""
    user = UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/deactivate", response_model=UserResponse)
def admin_deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMIN)),
):
    """Deactivate a user (admin only). Admin cannot deactivate themselves."""
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Admins cannot deactivate themselves")
    user = UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMIN)),
):
    """Permanently delete a user (admin only). Cannot delete self."""
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Admins cannot delete themselves")
    user = UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    UserService.delete_user_permanent(db, user_id)
    return {"message": "User permanently deleted", "user_id": user_id}
