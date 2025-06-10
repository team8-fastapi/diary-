# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from datetime import timedelta
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.token import Token  # Token 스키마 임포트
from app.crud.user import create_user, get_user_by_email  # 사용자 CRUD 함수 임포트
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.deps import get_db, get_current_user  # 의존성 주입 함수 임포트

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    hashed_password = get_password_hash(user_in.password)
    user_data = user_in.dict(exclude_unset=True)  # Pydantic v1, v2는 .model_dump()
    user_data["password"] = hashed_password
    user = create_user(db=db, user_data=user_data)
    return user


@auth_router.post("/login", response_model=Token)
async def login_for_access_token(user_in: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=user_in.email)
    if not user or not verify_password(user_in.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 토큰 페이로드에 사용자 ID 또는 이메일 등을 포함 (subject)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},  # 'sub' 클레임에 이메일 저장
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: UserResponse = Depends(get_current_user)):
    return current_user


# 로그아웃 기능 추가
@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: UserResponse = Depends(
        get_current_user
    ),  # 현재 로그인된 사용자 확인 (선택 사항)
    response: Response = None,  # 응답 헤더 조작을 위해 Response 객체 주입
):
    """
    사용자를 로그아웃합니다.

    이 함수는 클라이언트에게 저장된 JWT를 삭제하라는 신호를 보냅니다.
    서버 측에서는 특별한 상태 변경이 발생하지 않습니다 (JWT는 Stateless).
    """
    # 1. 클라이언트 측 로그아웃 (가장 일반적인 방법)
    # 서버는 단순히 204 No Content를 반환하여 클라이언트에게 성공적으로
    # 로그아웃되었음을 알리고, 클라이언트는 자신이 가지고 있는 JWT를 삭제합니다.
    # 즉, 이 엔드포인트는 클라이언트에게 "이제 토큰 지워!" 라고 알려주는 역할입니다.

    # 2. (선택 사항) 서버 측 블랙리스트 구현
    # 토큰 블랙리스트에 추가하는 로직이 있다면 여기에 구현합니다.
    # 예: add_token_to_blacklist(token_from_header)
    # 이 경우, get_current_user에서 토큰을 추출할 때 사용된 실제 JWT 문자열이 필요할 수 있습니다.
    # 하지만 OAuth2PasswordBearer는 직접 토큰 문자열을 반환하지 않으므로,
    # 필요하다면 다른 의존성 주입 방식을 사용하거나, token_from_header 인자를 추가해야 합니다.
    # 예: token: str = Depends(oauth2_scheme)

    # HTTP Only Cookie로 토큰을 저장했다면, 쿠키를 만료시키는 코드를 추가할 수 있습니다.
    # response.delete_cookie("access_token") # 쿠키 이름이 'access_token'일 경우

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# # (예시) 보호된 라우터
# @router.get("/protected-route")
# async def read_protected_data(current_user: UserResponse = Depends(get_current_user)):
#     return {"message": f"Hello, {current_user.email}! You accessed protected data."}
