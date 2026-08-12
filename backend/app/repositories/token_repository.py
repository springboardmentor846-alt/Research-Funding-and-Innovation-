import uuid
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class TokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, token: RefreshToken) -> RefreshToken:
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_by_token(self, token_str: str) -> Optional[RefreshToken]:
        query = select(RefreshToken).where(RefreshToken.token == token_str)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def revoke(self, token_obj: RefreshToken) -> None:
        token_obj.is_revoked = True
        await self.session.flush()

    async def revoke_all_user_tokens(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.is_revoked == False)
            .values(is_revoked=True)
        )
        await self.session.execute(stmt)
        await self.session.flush()
