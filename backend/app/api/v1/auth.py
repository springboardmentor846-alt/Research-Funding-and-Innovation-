from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.schemas.auth import (
    UserRegisterRequest,
    UserResponse,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    LogoutRequest,
    MessageResponse
)
from app.services.auth_service import AuthService

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
    data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    service = AuthService(db)
    user = await service.register_user(data)
    return user


@auth_router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    service = AuthService(db)
    user = await service.authenticate_user(email=data.email, password=data.password)
    return await service.create_tokens_for_user(user)


@auth_router.post(
    "/token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False
)
async def login_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    service = AuthService(db)
    user = await service.authenticate_user(email=form_data.username, password=form_data.password)
    return await service.create_tokens_for_user(user)


@auth_router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    service = AuthService(db)
    return await service.refresh_tokens(data.refresh_token)


@auth_router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK
)
async def logout(
    data: LogoutRequest,
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    service = AuthService(db)
    await service.logout(data.refresh_token)
    return MessageResponse(message="Successfully logged out")
