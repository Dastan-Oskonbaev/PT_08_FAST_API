from datetime import datetime, timezone
from typing import Optional, Tuple
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from apps.auth.repository import AuthRepository
from src.config import settings
from src.db.models import User
from src.security import hash_password, verify_password, create_jwt, decode_jwt


class AuthService:
    @staticmethod
    async def register(session: AsyncSession, *, email: EmailStr, password: str ) -> User:
        repo = AuthRepository(session)
        if await repo.find_user_by_email(email):
            raise ValueError("Email already exists")
        user = await repo.create_user(email=email, password=hash_password(password))
        return user


    @staticmethod
    async def authenticate(session: AsyncSession, *, email: EmailStr, password: str) -> Optional[User]:
        repo = AuthRepository(session)
        user = await AuthRepository.find_user_by_email(repo, email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    @staticmethod
    async def issue_token(session: AsyncSession, *, user: User) -> Tuple[str, str]:
        access = create_jwt(
            sub=str(user.id),
            token_type="access",
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

        refresh = create_jwt(
            sub=str(user.id),
            token_type="refresh",
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
        )
        payload = decode_jwt(refresh)
        jti = payload["jti"]
        exp = payload["exp"]
        expires_at = datetime.fromtimestamp(exp, tz = timezone.utc)
        repo = AuthRepository(session)
        await repo.save_refresh_token(jti=jti, user_id=user.id, expires_at=expires_at)
        return access, refresh

    @staticmethod
    async def refresh_access_token(session: AsyncSession, token: str) -> Tuple[str, str]:
        payload = decode_jwt(token)
        jti = payload["jti"]
        user_id = payload["sub"]

        repo = AuthRepository(session)
        row = await repo.get_refresh_token_by_jti(jti=jti)
        if not row:
            raise ValueError("Invalid refresh token")
        if row.revoked:
            raise ValueError("Refresh token has been revoked")
        if row.expires_at < datetime.now(timezone.utc):
            raise ValueError("Refresh token has expired")

        user = await repo.get_user_by_id(int(user_id))
        if not user:
            raise ValueError("Invalid user")

        await repo.delete_token(jti)
        new_access , new_refresh = await AuthService.issue_token(session, user=user)
        return new_access, new_refresh

    @staticmethod
    async def logout(session: AsyncSession, token: str):
        repo = AuthRepository(session)
        payload = decode_jwt(token)
        jti = payload["jti"]

        await repo.delete_token(jti)