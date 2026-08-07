"""
FastAPI dependencies for JWT authentication and RBAC.
"""
from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token
from app.database.session import get_db
from app.models.user import User, UserRole

bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validate the bearer token and return the authenticated user."""
    token = credentials.credentials
    payload = verify_token(token, "access")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str: str = payload.get("sub", "")
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject.",
        )

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )
    return user


async def get_current_active_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require the user's email to be verified."""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email address not verified. Please check your inbox.",
        )
    return current_user


def require_roles(*roles: UserRole):
    """Factory for RBAC role-gate dependencies."""

    async def _checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in roles and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access restricted. Required roles: {[r.value for r in roles]}",
            )
        return current_user

    return _checker


bearer_scheme_optional = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme_optional),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    if not credentials:
        return None
    try:
        token = credentials.credentials
        payload = verify_token(token, "access")
        if not payload:
            return None
        user_id = UUID(payload.get("sub", ""))
        user = await db.get(User, user_id)
        if user and user.is_active:
            return user
    except Exception:
        return None
    return None


# ── Shorthand role dependencies ───────────────────────────────────────────────
require_admin = require_roles(UserRole.ADMINISTRATOR)
require_manager_or_above = require_roles(
    UserRole.INNOVATION_MANAGER, UserRole.ADMINISTRATOR
)
require_any_authenticated = get_current_user

