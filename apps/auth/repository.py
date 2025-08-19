from datetime import datetime
from typing import Optional

from pydantic import EmailStr
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User, RefreshToken


class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_user_by_email(self, email: EmailStr) -> Optional[User]:
        q = await self.session.execute(select(User).where(User.email == email))
        return q.scalars().one_or_none()

    async def get_user_by_id(self, id_: int) -> Optional[User]:
        q = await self.session.execute(select(User).where(User.id == id_))
        return q.scalars().one_or_none()

    async def create_user(self, *, email: EmailStr, password: str) -> User:
        user = User(email=email, password=password)
        self.session.add(user)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise ValueError("Email already exists")
        await self.session.refresh(user)
        return user

    async def save_refresh_token(self, *, jti: str, user_id: int, expires_at: datetime) -> RefreshToken:
        token = RefreshToken(jti=jti, user_id=user_id, expires_at=expires_at, revoked=False)
        self.session.add(token)
        await self.session.commit()
        await self.session.refresh(token)
        return token

    async def get_refresh_token_by_jti(self, jti: str) -> Optional[RefreshToken]:
        q = await self.session.execute(select(RefreshToken).where(RefreshToken.jti == jti))
        return q.scalars().one_or_none()

    async def revoke_refresh_token(self, jti: str) -> None:
        token = await self.get_refresh_token_by_jti(jti)
        if token and not token.revoked:
            token.revoked = True
            await self.session.commit()

    async def revoke_if_exists(self, token: Optional[RefreshToken]):
        if token and not token.revoked:
            token.revoked = True
            await self.session.commit()


    async def delete_token(self, jti: str):
        await self.session.execute(delete(RefreshToken).where(RefreshToken.jti == jti))
        await self.session.commit()

