# app/deps.py
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.core.config import settings


from app.core.database import SessionFactory


from app.crud.user import get_user_by_email
from app.schemas.user import UserResponse

# JWT를 저장할 쿠키의 이름 (auth.py와 동일하게 유지)
ACCESS_TOKEN_COOKIE_NAME = "access_token"

# OAuth2PasswordBearer는 Swagger UI의 인증 설정에 사용됩니다.
# 실제 토큰 추출은 get_current_user에서 쿠키를 통해 직접 수행합니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # 로그인 엔드포인트 경로


def get_db():
    db = SessionFactory()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    request: Request, db: Session = Depends(get_db)
) -> UserResponse:
    token = request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")

        if email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = get_user_by_email(db, email=email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # 핵심 수정: ORM 객체에서 Pydantic 모델로 변환 시 from_attributes=True 사용
    return UserResponse.model_validate(user, from_attributes=True)  # Pydantic v2.x
    # Pydantic v1.x를 사용한다면 UserResponse.from_orm(user)를 계속 사용
