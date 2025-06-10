from fastapi import HTTPException
from rich import status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import UserCreate, Token, UserLogin, TokenRefresh
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)

BLACKLIST_REFRESH_TOKENS = set()


# 회원가입
def register(db: Session, user: UserCreate) -> User:
    existing = (
        db.query(User)
        .filter((User.email == user.email) | (User.name == user.username))
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="이미 사용중인 아이디/이메일 입니다.",
        )

    hashed_password = get_password_hash(user.password)

    new_user = User(name=user.username, email=user.email, password=hashed_password)

    # DB에 추가 및 저장
    db.add(new_user)
    db.commit()

    # DB에서 객체 불러오기
    db.refresh(new_user)

    return new_user


def login(db: Session, user: UserLogin) -> Token:
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호를 확인해주세요",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


def logout(refresh_token: str):
    BLACKLIST_REFRESH_TOKENS.add(refresh_token)


# 토큰 재발급 함수
def refresh_token(db: Session, token_refresh: TokenRefresh) -> Token:

    if token_refresh.refresh_token in BLACKLIST_REFRESH_TOKENS:
        raise HTTPException(status_code=401, detail="로그인을 해주세요")

    payload = decode_token(token_refresh.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="유효하지 않은 리프레시 토큰입니다")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="사용자 정보를 찾을 수 없습니다")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})

    BLACKLIST_REFRESH_TOKENS.add(token_refresh.refresh_token)

    return Token(
        access_token=access_token, refresh_token=new_refresh_token, token_type="bearer"
    )
