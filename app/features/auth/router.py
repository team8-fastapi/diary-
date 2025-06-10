from select import select

from fastapi import APIRouter, Depends, HTTPException, status
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
from app.features.auth.security import create_access_token
from app.features.auth.service import authenticate_user


auth_router = APIRouter()


@auth_router.post("/signup", response_model=SignupResponse)
async def signup(user_data: SignupRequest, db: AsyncSession = Depends(get_db)):
    # 중복 이메일 확인
    result = await db.execute(select(User).filter(User.email == user_data.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user_data.email,
        password=hash_password(user_data.password),
        name=user_data.name,
        phone_number=user_data.phone_number,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@auth_router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    access_token = create_access_token(data={"sub": str(user.user_id)})
    # refresh_token 구현 시 추가
    return TokenResponse(
        access_token=access_token, refresh_token="", token_type="bearer"
    )
