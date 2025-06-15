from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# 유저 정보/ 요청 본문
class UserCreate(BaseModel):
    email: EmailStr = Field(..., example="test@example.com")
    password: str = Field(..., min_length=8, example="password123!")
    name: str = Field(..., min_length=2, example="<NAME>")
    phone_number: Optional[str] = Field(None, example="010-1234-5678")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, example="<NAME>")
    phone_number: Optional[str] = Field(None, example="010-1234-5678")
    password: Optional[str] = Field(None, min_length=8, example="password123!")


class UserResponse(BaseModel):
    user_id: int = Field(..., example=1)
    email: EmailStr = Field(..., example="test@example.com")
    name: str = Field(..., example="홍길동")
    phone_number: Optional[str] = Field(None, example="010-1234-5678")
    last_login: Optional[datetime] = Field(None, example="2025-06-10T15:00:00Z")
    is_staff: bool = Field(False, example=False)
    is_admin: bool = Field(False, example=False)
    is_active: bool = Field(True, example=True)
    created_at: datetime = Field(..., example="2025-06-01T10:00:00Z")
    updated_at: datetime = Field(..., example="2025-06-09T14:30:00Z")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Config:
    from_attributes = True
