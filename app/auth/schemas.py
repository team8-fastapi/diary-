from pydantic import BaseModel, EmailStr


# 회원가입 요청
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone_number: str | None = None  # 없으면 None


# 회원가입 응답
class SignupResponse(BaseModel):
    user_id: int
    email: EmailStr
    name: str
    phone_number: str | None
    is_active: bool

    class Config:
        # ORM 객체에서 데이터를 읽어올 수 있게 해줌 (ex: SQLAlchemy model → Pydantic model 자동 변환)
        orm_mode = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
