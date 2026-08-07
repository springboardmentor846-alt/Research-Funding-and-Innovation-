"""
Authentication API router — register, login, refresh, logout, password reset.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import (
    AccessTokenResponse,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description=(
        "Create a new platform account. "
        "A verification email is sent if email sending is configured."
    ),
)
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    service = AuthService(db)
    user = await service.register(payload)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and obtain JWT token pair",
    description="Exchange valid credentials for an access token and a refresh token.",
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    service = AuthService(db)
    return await service.login(payload.email, payload.password)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Rotate refresh token and obtain a new access token",
    description=(
        "Exchange a valid refresh token for a new access + refresh token pair. "
        "The old refresh token is revoked (token rotation)."
    ),
)
async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    service = AuthService(db)
    return await service.refresh_access_token(payload.refresh_token)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout and revoke refresh token",
)
async def logout(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> MessageResponse:
    service = AuthService(db)
    await service.logout(payload.refresh_token)
    return MessageResponse(message="Successfully logged out.")


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request a password reset link",
    description=(
        "Send a password reset email if the address is registered. "
        "Always returns 200 to prevent user enumeration."
    ),
)
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    service = AuthService(db)
    await service.forgot_password(payload.email)
    return MessageResponse(
        message="If that email is registered, a reset link has been sent."
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password using the emailed token",
)
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    from fastapi import HTTPException, status as st

    if payload.new_password != payload.confirm_password:
        raise HTTPException(
            status_code=st.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Passwords do not match.",
        )
    service = AuthService(db)
    await service.reset_password(payload.token, payload.new_password)
    return MessageResponse(message="Password has been reset successfully.")


@router.post(
    "/verify-email",
    response_model=MessageResponse,
    summary="Verify email address using the emailed token",
)
async def verify_email(
    payload: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    service = AuthService(db)
    await service.verify_email(payload.token)
    return MessageResponse(message="Email verified successfully.")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
)
async def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)
