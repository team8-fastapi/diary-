from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
    username: str = Field(..., min_length=5, max_length=20, example="username")
    email: EmailStr = Field(..., example="abcd@example.com")
    password: str = Field(..., min_length=8, max_length=64, example="PASSWORD")


# 로그인 및 회원가입 후 반환되는 토큰
class Token(BaseModel):
    access_token: str
    token_type: str = Field("Bearer", const=True)
    refresh_token: str


# Refresh 토큰 재발급
class TokenRefresh(BaseModel):
    refresh_token: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class UserOut(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True
