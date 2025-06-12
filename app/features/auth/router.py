from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.features.auth.service import signup_user, login_user, logout_user
from app.core.deps import get_db
from app.features.user.schemas import UserResponse, UserCreate

auth_router = APIRouter()


# 회원가입
@auth_router.post("/signup", response_model=UserResponse)
async def signup(user_in: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    return signup_user(user_in, db)


# 로그인
@auth_router.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return login_user(response, form_data, db)


@auth_router.post("/logout", status_code=204)
async def logout(response: Response):
    return logout_user(response)
