from fastapi import APIRouter, HTTPException, Request
from request import UserSignUpRequest, UserLoginRequest
from authentication import hash_password, verify_password
from user.models import User
from database import SessionFactory
from authorization import create_access_token, create_refresh_token
from user.models import kstnow, RefreshToken
from datetime import timedelta

router = APIRouter(tags=["User"])


# 📌 회원가입 API
@router.post("/users/sign-up", status_code=201)
def user_sign_up_handler(body: UserSignUpRequest):
    # 1) 사용자 정보 입력 / 필수 정보 체크 / 이메일 형식 유효성 검사 / 비밀번호 보안 조건 확인 = UserSignUpRequest
    session = SessionFactory()
    try:
        # 2) 이메일 중복 확인
        if user := session.query(User).filter(User.email == body.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")

        # 2) 데이터를 user 테이블에 저장함.
        hashed_password = hash_password(plain_password=body.password)
        user_data = body.model_dump()
        user_data["password"] = hashed_password
        new_user = User(**user_data)

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        # 3) 응답 반환
        return {
            "user_id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "phone_number": new_user.phone_number,
            "username": new_user.username,
        }

    finally:
        session.close()


# 📌 로그인 API
@router.post("/users/login")
def user_login_handler(body: UserLoginRequest):
    # 1) 입력값 유효성 검사 = UserLoginRequest
    session = SessionFactory()
    try:
        # 2) 사용자 정보를 email을 기준으로 조회 (해시값)
        if not (user := session.query(User).filter_by(email=body.email).first()):
            raise HTTPException(status_code=404, detail="User not found")

        # 3) password <-> hashed password 비교
        if not verify_password(plain_password=body.password, hashed=user.password):
            raise HTTPException(status_code=404, detail="Incorrect email or password")

        # 4) JWT 토큰 발급
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30)
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}, expires_delta=timedelta(days=7)
        )

        expires_at = kstnow() + timedelta(days=7)

        # 5) DB에 클라이언트 토큰 저장
        session.add(
            RefreshToken(
                user_id=user.id, token=refresh_token, expires_at=expires_at, used=False
            )
        )
        session.commit()

        # 6) 응답 반환
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    finally:
        session.close()


# 📌 로그아웃 API
@router.post("/users/logout")
def user_logout_handler(request: Request):
    session = SessionFactory()
    try:
        # 클라이언트 토큰 무효화
        refresh_token = request.headers.get("X-Refresh-Token")
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Refresh token required")

        token_obj = (
            session.query(RefreshToken)
            .filter_by(token=refresh_token, used=False)
            .first()
        )
        if not token_obj:
            raise HTTPException(
                status_code=400, detail="Invalid or already logged out refresh token"
            )

        token_obj.used = True
        session.commit()

        return {"detail": "Successfully logged out"}

    finally:
        session.close()


# 토큰 재발급시 로직
