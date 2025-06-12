from fastapi import HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.features.auth.repository import get_user_by_email, create_user
from app.features.auth.authentication import (
    verify_password,
    get_password_hash,
    create_access_token,
)
from app.core.config import settings
from app.features.user.schemas import UserCreate


# 회원가입
def signup_user(user_in: UserCreate, db: Session):
    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user_data = user_in.dict(exclude_unset=True)
    user_data["password"] = get_password_hash(user_in.password)
    return create_user(db, user_data)


# 로그인
def login_user(response: Response, form_data: OAuth2PasswordRequestForm, db: Session):
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data={"sub": user.email}, expires_delta=token_expires)
    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="Lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        domain="127.0.0.1",
    )
    return {"message": "Logged in successfully"}


# 로그아웃
def logout_user(response: Response):
    response.delete_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        httponly=True,
        samesite="Lax",
        path="/",
        domain="127.0.0.1",
    )
