from sqlalchemy import select

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.auth.schemas import (
    SignupRequest,
    SignupResponse,
    LoginRequest,
    TokenResponse,
)
from app.core.dependencies import get_db
from app.features.user.models import User
from app.features.auth.hashing import hash_password
from app.features.auth.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.features.auth.service import authenticate_user


auth_router = APIRouter()


@auth_router.post("/signup", response_model=SignupResponse)
async def signup(user_data: SignupRequest, db: AsyncSession = Depends(get_db)) -> SignupResponse:
    # 중복 이메일 확인
    result = await db.execute(select(User).filter(User.email == user_data.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 비밀번호 해시 처리 및 새로운 사용자 생성
    new_user = User(
        email=user_data.email,
        password=hash_password(user_data.password),
        name=user_data.name,
        phone_number=user_data.phone_number,
    )

    # DB에 저장
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@auth_router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    access_token = create_access_token(data={"sub": str(user.user_id)})
    # refresh_token 구현 시 추가

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False,  # HTTPS 환경에서는 True로
    )

    return TokenResponse(
        access_token=access_token, refresh_token="", token_type="bearer"
    )

