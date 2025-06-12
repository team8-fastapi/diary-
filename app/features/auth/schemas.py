from typing import Optional

from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None  # 토큰 페이로드에 들어갈 정보 (예: 사용자 ID)
    email: Optional[str] = None  # 페이로드에 이메일도 포함 가능
