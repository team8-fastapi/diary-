# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

# 필요한 스키마, CRUD, 보안 관련 함수들 임포트
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.crud.user import create_user, get_user_by_email, update_user, delete_user
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.deps import get_db, get_current_user

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

ACCESS_TOKEN_COOKIE_NAME = "access_token"


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
    user_data = user_in.dict(exclude_unset=True)
    user_data["password"] = hashed_password
    user = create_user(db=db, user_data=user_data)
    return user


@auth_router.post("/login")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires,
    )

    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        httponly=True,
        samesite="Lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        domain="127.0.0.1",
        # secure=True # 프로덕션 환경에서 HTTPS를 사용한다면 이 줄의 주석을 해제하세요.
    )

    return {"message": "Logged in successfully"}


@auth_router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: UserResponse = Depends(get_current_user)):
    """
    로그인 유저 정보 조회
    """
    return current_user


@auth_router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_in: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    로그인한 유저 정보 수정 기능
    """
    db_user_to_update = get_user_by_email(db, email=current_user.email)
    if not db_user_to_update:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = update_user(db=db, db_user=db_user_to_update, user_in=user_in)

    return updated_user


@auth_router.delete("/me")  # status_code=status.HTTP_204_NO_CONTENT 제거
async def delete_current_user(
    response: Response,  # 응답 쿠키 삭제를 위해 Response 객체 주입
    current_user: UserResponse = Depends(get_current_user),  # 현재 로그인된 사용자 확인
    db: Session = Depends(get_db),  # DB 세션 주입
):
    """
    현재 로그인된 사용자의 계정을 삭제합니다.
    """
    user_deleted = delete_user(
        db, user_id=current_user.user_id
    )  # user_id는 Pydantic UserResponse에서 가져옴

    if not user_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or could not be deleted",
        )

    # 계정 삭제 성공 후, 사용자 세션(쿠키)도 삭제
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        httponly=True,
        samesite="Lax",
        path="/",
        domain="127.0.0.1",
        # secure=True # 프로덕션 환경에서 HTTPS를 사용한다면 이 줄의 주석을 해제하세요.
    )
    # Refresh Token도 사용한다면 여기서 삭제 로직 추가 (블랙리스트 포함)
    # response.delete_cookie(key=REFRESH_TOKEN_COOKIE_NAME, ...)

    # 204 No Content 대신 "Deleted successfully" 메시지 반환
    return {"message": "Deleted successfully"}


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):  # Response 객체를 인자로 받음
    """
    사용자를 로그아웃합니다.

    이 함수는 HTTP Only 쿠키에 저장된 JWT 토큰(access_token)을 삭제하여 클라이언트의 세션을 종료합니다.
    """
    # Access Token 쿠키 삭제 지시를 response 객체에 추가
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        httponly=True,
        samesite="Lax",
        path="/",
        domain="127.0.0.1",
        # secure=True # 프로덕션 환경에서 HTTPS를 사용한다면 이 줄의 주석을 해제하세요.
    )
    # 함수가 명시적으로 응답 본문을 반환하지 않으므로, FastAPI는 status_code=204에 맞춰 적절한 응답을 생성하고
    # response 객체에 추가된 Set-Cookie 헤더를 포함시킬 것입니다.
    # return Response(status_code=status.HTTP_204_NO_CONTENT) # 이 줄은 삭제 또는 주석 처리!
    pass  # 아무것도 명시적으로 반환하지 않으면 FastAPI가 204 No Content에 맞춰 응답을 생성합니다.
