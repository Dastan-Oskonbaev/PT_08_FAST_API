from datetime import datetime, timezone, timedelta
from typing import Literal, Optional, Dict
from uuid import uuid4

from fastapi import Depends
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.annotation import Annotated

from src.config import settings
from src.db.models import User
from src.db.session import get_session

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

def create_jwt(*, sub: str, token_type: Literal["access", "refresh"] = "access",
               minutes: Optional[int] = None, days: Optional[int] = None,
               extra_claims: Optional[Dict] = None) -> str:
    now = _now_utc()
    if minutes is not None:
        exp = now + timedelta(minutes=minutes)
    elif days is not None:
        exp = now + timedelta(days=days)
    else:
        raise ValueError("Either minutes or days must be specified")
    payload = {
        "sub": sub,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "nbf": int(now.timestamp()),
    }

    if token_type == "refresh":
        payload["jti"] = str(uuid4())

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_access_token(*, sub: str) -> str:
    return create_jwt(sub=sub, token_type="access", minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

def create_refresh_token(*, sub: str) -> str:
    return create_jwt(sub=sub, token_type="refresh", days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

def decode_jwt(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

async def get_current_user(token: Annotated[str, Depends(lambda authorization: _bearer_extractor(authorization))],
                     session: Annotated[AsyncSession, Depends(get_session)]) -> User:
    try:
        payload = decode_jwt(token)
        if payload["type"] != "access":
            raise ValueError("Invalid token type")
        user_id = int(payload["sub"])
    except Exception as e:
        raise ValueError("Invalid token") from e

    result = await session.execute(select(User).where(User.id == user_id).limit(1))
    user = result.scalars().one_or_none()
    if not user:
        raise ValueError("Invalid user")
    return user


def _bearer_extractor(authorization: str) -> str:
    if not authorization:
        raise ValueError("Authorization header is missing")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise ValueError("Invalid authorization header")
    return parts[1]