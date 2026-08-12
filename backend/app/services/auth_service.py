from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import TokenType
from app.core.security import (
    create_token,
    decode_token,
    get_password_hash,
    verify_password
)
from app.core.exceptions import AuthenticationException, BaseAppException
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository
from app.schemas.auth import UserRegisterRequest, TokenResponse


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.token_repo = TokenRepository(session)

    async def register_user(self, data: UserRegisterRequest) -> User:
        existing_user = await self.user_repo.get_by_email(data.email)
        if existing_user:
            raise BaseAppException(
                message="User with this email already exists",
                status_code=400
            )

        hashed_pw = get_password_hash(data.password)
        user = User(
            email=data.email,
            hashed_password=hashed_pw,
            full_name=data.full_name,
            role=data.role
        )
        return await self.user_repo.create(user)

    async def authenticate_user(self, email: str, password: str) -> User:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationException(message="Invalid email or password")

        if not user.is_active:
            raise AuthenticationException(message="User account is inactive")

        user.last_login = datetime.now(timezone.utc)
        await self.user_repo.update(user)
        return user

    async def create_tokens_for_user(self, user: User) -> TokenResponse:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        access_token = create_token(
            subject=str(user.id),
            token_type=TokenType.ACCESS,
            expires_delta=access_token_expires,
            additional_claims={"role": user.role.value, "email": user.email}
        )

        refresh_token = create_token(
            subject=str(user.id),
            token_type=TokenType.REFRESH,
            expires_delta=refresh_token_expires
        )

        expires_at = datetime.now(timezone.utc) + refresh_token_expires
        token_obj = RefreshToken(
            token=refresh_token,
            user_id=user.id,
            expires_at=expires_at
        )
        await self.token_repo.create(token_obj)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    async def refresh_tokens(self, refresh_token_str: str) -> TokenResponse:
        payload = decode_token(refresh_token_str)
        if not payload or payload.get("type") != TokenType.REFRESH.value:
            raise AuthenticationException(message="Invalid or expired refresh token")

        db_token = await self.token_repo.get_by_token(refresh_token_str)
        if not db_token or db_token.is_revoked:
            raise AuthenticationException(message="Refresh token is revoked or invalid")

        if db_token.expires_at.tzinfo is None:
            db_token_expires_at = db_token.expires_at.replace(tzinfo=timezone.utc)
        else:
            db_token_expires_at = db_token.expires_at

        if db_token_expires_at < datetime.now(timezone.utc):
            await self.token_repo.revoke(db_token)
            raise AuthenticationException(message="Refresh token has expired")

        await self.token_repo.revoke(db_token)

        user = await self.user_repo.get_by_id(db_token.user_id)
        if not user or not user.is_active:
            raise AuthenticationException(message="User associated with token is inactive or not found")

        return await self.create_tokens_for_user(user)

    async def logout(self, refresh_token_str: str) -> None:
        db_token = await self.token_repo.get_by_token(refresh_token_str)
        if db_token and not db_token.is_revoked:
            await self.token_repo.revoke(db_token)
