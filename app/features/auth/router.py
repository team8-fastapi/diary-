from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.auth.schemas import (
    SignupRequest,
    SignupResponse,
    LoginRequest,
    TokenResponse,
)
from app.core.dependencies import get_db
from app.features.auth.Authentication import (
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.features.auth.service import authenticate_user, signup_user

auth_router = APIRouter()


@auth_router.post("/signup", response_model=SignupResponse)
async def signup(
    user_data: SignupRequest, db: AsyncSession = Depends(get_db)
) -> SignupResponse:
    try:
        user = await signup_user(db, user_data)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)
):
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
