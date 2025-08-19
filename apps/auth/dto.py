from datetime import datetime

from pydantic import EmailStr, Field, ConfigDict, BaseModel


class UserCreateDto(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=255)

class UserOutDto(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TokenPairDto(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class AccessTokenDto(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RefreshTokenDto(BaseModel):
    refresh_token: str