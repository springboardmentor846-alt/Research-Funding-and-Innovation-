"""
Authentication service — register, login, token refresh, password reset.
"""
import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
    create_password_reset_token,
)
from app.models.user import RefreshToken, User
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate
from app.utils.email import send_password_reset_email, send_verification_email

logger = logging.getLogger(__name__)


def _hash_token(token: str) -> str:
    """SHA-256 hash a JWT before storing (tokens are opaque secrets)."""
    return hashlib.sha256(token.encode()).hexdigest()


class AuthService:
    """Business logic for all authentication flows."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Register ──────────────────────────────────────────────────────────────
    async def register(self, data: UserCreate) -> User:
        """Create a new user account."""
        # Check duplicate
        existing = await self._get_user_by_email(data.email)
        if existing:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )

        verification_token = secrets.token_urlsafe(32)
        user = User(
            email=data.email.lower(),
            full_name=data.full_name,
            hashed_password=get_password_hash(data.password),
            role=data.role,
            verification_token=verification_token,
            is_active=True,
            is_verified=False,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        # Send verification email (non-blocking; errors are logged)
        if settings.EMAILS_ENABLED:
            try:
                await send_verification_email(user.email, verification_token)
            except Exception as exc:
                logger.warning(f"Verification email failed for {user.email}: {exc}")

        logger.info(f"New user registered: {user.email} | role={user.role}")
        return user

    # ── Login ─────────────────────────────────────────────────────────────────
    async def login(self, email: str, password: str) -> TokenResponse:
        """Authenticate credentials and return a token pair."""
        from fastapi import HTTPException, status

        user = await self._get_user_by_email(email.lower())
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated.",
            )

        tokens = await self._issue_token_pair(user)

        # Update last login
        user.last_login = datetime.now(timezone.utc)
        user.login_count = (user.login_count or 0) + 1
        await self.db.commit()

        return tokens

    # ── Refresh ───────────────────────────────────────────────────────────────
    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Exchange a valid refresh token for a new token pair (rotation)."""
        from fastapi import HTTPException, status

        payload = verify_token(refresh_token, "refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token.",
            )

        # Look up stored token
        token_hash = _hash_token(refresh_token)
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        stored = result.scalar_one_or_none()
        if not stored or stored.revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found or already revoked.",
            )
        expires_at = stored.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired.",
            )

        # Revoke old token (rotation)
        stored.revoked = True
        await self.db.commit()

        user = await self.db.get(User, stored.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive.",
            )

        return await self._issue_token_pair(user)

    # ── Logout ────────────────────────────────────────────────────────────────
    async def logout(self, refresh_token: str) -> None:
        """Revoke the provided refresh token."""
        token_hash = _hash_token(refresh_token)
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        stored = result.scalar_one_or_none()
        if stored:
            stored.revoked = True
            await self.db.commit()

    # ── Forgot Password ───────────────────────────────────────────────────────
    async def forgot_password(self, email: str) -> None:
        """
        Generate a password-reset token and send it by email.
        Always returns success to avoid user enumeration.
        """
        user = await self._get_user_by_email(email.lower())
        if not user:
            return  # Silent — don't reveal if email exists

        reset_token = create_password_reset_token(email)
        user.password_reset_token = _hash_token(reset_token)
        user.password_reset_expires = datetime.now(timezone.utc) + timedelta(
            hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
        )
        await self.db.commit()

        if settings.EMAILS_ENABLED:
            try:
                await send_password_reset_email(user.email, reset_token)
            except Exception as exc:
                logger.warning(f"Password-reset email failed for {email}: {exc}")

    # ── Reset Password ────────────────────────────────────────────────────────
    async def reset_password(self, token: str, new_password: str) -> None:
        """Validate the reset token and update the user's password."""
        from fastapi import HTTPException, status

        payload = verify_token(token, "password_reset")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password reset token.",
            )

        email = payload.get("sub")
        user = await self._get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )

        token_hash = _hash_token(token)
        if user.password_reset_token != token_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password reset token.",
            )
        if user.password_reset_expires and user.password_reset_expires < datetime.now(
            timezone.utc
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password reset token has expired.",
            )

        user.hashed_password = get_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        await self.db.commit()

    # ── Verify Email ──────────────────────────────────────────────────────────
    async def verify_email(self, token: str) -> None:
        """Mark the user's email as verified."""
        from fastapi import HTTPException, status

        result = await self.db.execute(
            select(User).where(User.verification_token == token)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token.",
            )

        user.is_verified = True
        user.verification_token = None
        await self.db.commit()

    # ── Helpers ───────────────────────────────────────────────────────────────
    async def _get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def _issue_token_pair(self, user: User) -> TokenResponse:
        """Create access + refresh tokens and persist the refresh token."""
        extra_claims = {"role": user.role.value, "email": user.email}
        access_token = create_access_token(str(user.id), extra_claims=extra_claims)
        refresh_token = create_refresh_token(str(user.id))

        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        token_record = RefreshToken(
            token_hash=_hash_token(refresh_token),
            user_id=user.id,
            expires_at=expires_at,
        )
        self.db.add(token_record)
        await self.db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
        )
