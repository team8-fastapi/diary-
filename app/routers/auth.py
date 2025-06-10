from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.auth import UserLogin, UserCreate, TokenRefresh, Token
from app.services.auth import register, login, logout, refresh_token
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserLogin)
def api_register(user: UserCreate, db: Session = Depends(get_db)):
    return register(db, user)


@router.post("/login", response_model=Token)
def api_login(user: UserLogin, db: Session = Depends(get_db)):
    return login(db, user)


@router.post("/logout")
def api_logout(
    token_refresh: TokenRefresh,
):
    logout(token_refresh.refresh_token)
    return {"message": "로그아웃 하였습니다."}


@router.post("/refresh", response_model=Token)
def api_refresh(token_refresh: TokenRefresh, db: Session = Depends(get_db)):
    return refresh_token(db, token_refresh)
