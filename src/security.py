from datetime import datetime, timezone, timedelta
from typing import Literal, Optional, Dict, Annotated
from uuid import uuid4

from fastapi import Depends, HTTPException, Header
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

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

def bearer_token_from_header(
    authorization: Annotated[str | None, Header()] = None
) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    scheme, _, param = authorization.partition(" ")
    if scheme.lower() != "bearer" or not param:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return param

# твоя зависимость получения пользователя из токена
async def get_current_user(
    token: Annotated[str, Depends(bearer_token_from_header)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    try:
        payload = decode_jwt(token)
        if payload.get("type") != "access":
            raise ValueError("Invalid token type")
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await session.execute(select(User).where(User.id == user_id).limit(1))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
