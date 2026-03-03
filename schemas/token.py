from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None


class RefreshToken(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int