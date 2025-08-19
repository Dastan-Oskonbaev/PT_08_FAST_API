from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from apps.auth.dto import UserOutDto, UserCreateDto, TokenPairDto, RefreshTokenDto
from apps.auth.service import AuthService
from src.db.session import get_session

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOutDto, status_code=status.HTTP_201_CREATED)
async def register(body: UserCreateDto, session: Annotated[AsyncSession, Depends(get_session)]):
    try:
        user = await AuthService.register(session, email=body.email, password=body.password)
        return UserOutDto.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenPairDto)
async def login(body: UserCreateDto, session: Annotated[AsyncSession, Depends(get_session)]):
    user = await AuthService.authenticate(session, email=body.email, password=body.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access, refresh = await AuthService.issue_token(session, user=user)
    return TokenPairDto(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenPairDto)
async def refresh(body: RefreshTokenDto, session: Annotated[AsyncSession, Depends(get_session)]):
    try:
        new_access, new_refresh = await AuthService.refresh_access_token(session, token=body.refresh_token)
        return TokenPairDto(access_token=new_access, refresh_token=new_refresh)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/logout")
async def logout(body: RefreshTokenDto, session: Annotated[AsyncSession, Depends(get_session)]):
    try:
        await AuthService.logout(session, token=body.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
