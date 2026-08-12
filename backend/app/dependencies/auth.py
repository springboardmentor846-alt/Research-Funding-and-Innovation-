"""
Authentication & Role-Based Access Control (RBAC) Dependency Providers
"""

from typing import Dict, List, Any
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.constants import UserRole, TokenType
from app.core.security import decode_token
from app.core.exceptions import AuthenticationException, PermissionDeniedException
from app.dependencies.db import get_db

# OAuth2 Bearer Scheme pointing to token endpoint
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token"
)


async def get_current_user_claims(
    token: str = Depends(reusable_oauth2)
) -> Dict[str, Any]:
    """
    Validates incoming JWT bearer token and extracts token claims payload.
    """
    payload = decode_token(token)
    if not payload:
        raise AuthenticationException(message="Invalid or expired access token")

    token_type = payload.get("type")
    if token_type != TokenType.ACCESS.value:
        raise AuthenticationException(message="Invalid token type for access authentication")

    user_id: str = payload.get("sub")
    if not user_id:
        raise AuthenticationException(message="Token payload missing subject identifier")

    return payload


async def get_current_user(
    claims: Dict[str, Any] = Depends(get_current_user_claims),
    db: AsyncSession = Depends(get_db)
):
    """
    Resolves the authenticated User ORM object from the database using JWT claims.
    """
    from app.models.user import User

    user_id = claims.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user or not user.is_active:
        raise AuthenticationException(message="User not found or inactive")

    return user


class RoleChecker:
    """
    Role-Based Access Control (RBAC) Guard Dependency Class.
    Usage: Depends(RoleChecker([UserRole.SYSTEM_ADMIN, UserRole.RESEARCHER]))
    """
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = [role.value for role in allowed_roles]

    def __call__(self, claims: Dict[str, Any] = Depends(get_current_user_claims)) -> Dict[str, Any]:
        user_role = claims.get("role")
        if not user_role or user_role not in self.allowed_roles:
            raise PermissionDeniedException(
                message=f"Access denied. Requires one of roles: {self.allowed_roles}"
            )
        return claims
