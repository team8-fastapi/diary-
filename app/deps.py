# app/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.security import decode_access_token

# app/crud/user.py 에서 사용자 조회 함수를 임포트
from app.crud.user import get_user_by_email  # 또는 get_user_by_id
from app.schemas.user import UserResponse

# OAuth2PasswordBearer는 "/token" 엔드포인트에서 토큰을 가져올 것을 기대합니다.
# 실제로는 로그인 엔드포인트에서 토큰을 발급하고, 이 의존성은 후속 요청에서 토큰을 검증합니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")  # 로그인 엔드포인트 경로


def get_db():
    # 데이터베이스 세션 생성 및 종료 로직
    # (이는 app/core/database.py에 정의되어야 함)
    # yield SessionLocal()
    pass  # 실제 구현으로 대체


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # 토큰 디코딩
    token_data = decode_access_token(token)
    if token_data is None:
        raise credentials_exception

    # 토큰 데이터에서 사용자 정보 추출
    # (예: user_id 또는 email)
    if not token_data.get("sub"):  # 'sub' 클레임에 user_id나 email이 저장되었다고 가정
        raise credentials_exception

    # 데이터베이스에서 사용자 조회
    user = get_user_by_email(db, email=token_data["sub"])  # 'sub'에 이메일 저장 시
    # user = get_user_by_id(db, user_id=token_data["sub"]) # 'sub'에 user_id 저장 시

    if user is None:
        raise credentials_exception
    return user  # Pydantic UserResponse 모델로 변환하여 반환하는 것이 좋음


# (옵션) 관리자 권한 확인 의존성
async def get_current_admin_user(
    current_user: UserResponse = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user
