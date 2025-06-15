import os
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import httpx  # 외부 HTTP 요청을 위한 라이브러리
from urllib.parse import urlparse, urlencode  # URL 인코딩을 위해 필요
import secrets  # state 값 생성을 위해 필요

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
    """
    일반 이메일/비밀번호 기반 회원가입
    """
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
    """
    일반 이메일/비밀번호 기반 로그인
    JWT access_token을 HTTP Only 쿠키로 설정합니다.
    """
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
        domain=None,
        # secure=True # 프로덕션 환경에서 HTTPS를 사용한다면 이 줄의 주석을 해제하세요.
    )

    return {"message": "Logged in successfully"}


@auth_router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: UserResponse = Depends(get_current_user)):
    """
    로그인된 유저 정보 조회
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


@auth_router.delete("/me")
async def delete_current_user(
        response: Response,
        current_user: UserResponse = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    """
    현재 로그인된 사용자의 계정을 삭제합니다.
    """
    user_deleted = delete_user(db, user_id=current_user.user_id)

    if not user_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or could not be deleted",
        )

    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        httponly=True,
        samesite="Lax",
        path="/",
        domain=None,
        # secure=True # 프로덕션 환경에서 HTTPS를 사용한다면 이 줄의 주석을 해제하세요.
    )
    return {"message": "Deleted successfully"}


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    """
    사용자를 로그아웃합니다.
    이 함수는 HTTP Only 쿠키에 저장된 JWT 토큰(access_token)을 삭제하여 클라이언트의 세션을 종료합니다.
    """
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        httponly=True,
        samesite="Lax",
        path="/",
        domain=None,
        # secure=True # 프로덕션 환경에서 HTTPS를 사용한다면 이 줄의 주석을 해제하세요.
    )
    pass


# --- Google 소셜 로그인 시작 엔드포인트 ---
@auth_router.get("/google/login")
async def google_login(response: Response):
    """
    Google OAuth 2.0 로그인 흐름을 시작합니다.
    사용자를 Google 권한 부여 서버로 리디렉션합니다.
    state 값은 브라우저 쿠키에 저장됩니다.
    """
    state = secrets.token_urlsafe(16)

    # state 값을 브라우저 쿠키에 저장 (CSRF 방지)
    # HTTP 환경에서 SameSite=Lax는 동작해야 하지만, 특정 브라우저나 환경에서 제한이 있을 수 있습니다.
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        samesite="Lax",  # HTTP 환경에서 일반적으로 권장되는 설정
        path="/",
        domain=None,  # 브라우저가 현재 호스트 도메인을 사용하도록 함 (가장 유연)
        # secure=True # 프로덕션 환경에서 HTTPS를 사용한다면 이 줄의 주석을 해제하세요.
    )
    print(f"DEBUG: Setting oauth_state cookie for Google with value: {state}")

    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI")
    scope = "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile openid"

    auth_url_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,  # state 값을 URL 파라미터로 전달
        "access_type": "offline",
        "prompt": "consent"
    }
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(auth_url_params)}"

    raise HTTPException(status_code=status.HTTP_302_FOUND, headers={"Location": auth_url})


# --- Google 소셜 로그인 콜백 엔드포인트 ---
@auth_router.get("/google/callback")
async def google_callback(
        code: str,  # Google에서 전달하는 authorization code
        state: str,  # Google에서 전달하는 state 값
        response: Response,
        request: Request,
        db: Session = Depends(get_db)
):
    """
    Google OAuth 2.0 콜백 엔드포인트.
    authorization code를 받아 access_token으로 교환하고 사용자 정보를 처리합니다.
    state 값은 브라우저 쿠키에서 검증됩니다.
    """
    # 1. state 값 검증 (CSRF 방지) - 브라우저 쿠키에서 조회
    stored_state = request.cookies.get("oauth_state")
    print(f"DEBUG: Stored Google state from cookie: {stored_state}, Received state from URL: {state}")

    if not stored_state or stored_state != state:
        print("DEBUG: Invalid Google state parameter detected.")
        if not stored_state:
            print("DEBUG: 'oauth_state' cookie was not found for Google.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter"
        )

    response.delete_cookie(key="oauth_state", path="/")  # 사용한 state 쿠키 삭제
    print(f"DEBUG: Google state '{state}' validated and cookie deleted.")

    # 2. authorization_code를 access_token으로 교환
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI")

    token_url = "https://oauth2.googleapis.com/token"
    token_params = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }

    try:
        async with httpx.AsyncClient() as client:
            token_res = await client.post(token_url, data=token_params)
            token_res.raise_for_status()
            token_data = token_res.json()
    except httpx.HTTPStatusError as e:
        print(f"Error getting token from Google: {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to exchange code for token: {e.response.text}"
        )
    except httpx.RequestError as e:
        print(f"Network error during token exchange: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Network error during token exchange with Google"
        )

    access_token = token_data.get("access_token")

    if not access_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Failed to get access token from Google response")

    # 3. access_token으로 사용자 프로필 정보 요청
    userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        async with httpx.AsyncClient() as client:
            userinfo_res = await client.get(userinfo_url, headers=headers)
            userinfo_res.raise_for_status()
            user_profile = userinfo_res.json()
    except httpx.HTTPStatusError as e:
        print(f"Error getting user info from Google: {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to get user info from Google: {e.response.text}"
        )
    except httpx.RequestError as e:
        print(f"Network error during user info request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Network error during user info request with Google"
        )

    user_email = user_profile.get("email")
    user_name = user_profile.get("name", user_email)

    if not user_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not retrieve user email from Google")

    # 4. 우리 서비스에 사용자 가입 또는 로그인 처리
    db_user = get_user_by_email(db, email=user_email)
    if not db_user:
        new_user_data = {
            "email": user_email,
            "name": user_name,
            "password": get_password_hash(secrets.token_urlsafe(32)),
        }
        user_create_schema = UserCreate(**new_user_data)
        db_user = create_user(db=db, user_in=user_create_schema)

    # 5. 우리 서비스의 JWT 토큰 발급 및 쿠키 설정
    our_access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    our_access_token = create_access_token(
        data={"sub": db_user.email},
        expires_delta=our_access_token_expires,
    )
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=our_access_token,
        httponly=True,
        samesite="Lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        domain=None,
    )

    # 6. 프론트엔드로 리디렉션 (로그인 성공 페이지 등)
    frontend_redirect_url = os.environ.get("APP_FRONTEND_URL", "/")
    raise HTTPException(status_code=status.HTTP_302_FOUND, headers={"Location": frontend_redirect_url})


# --- 네이버 소셜 로그인 시작 엔드포인트 ---
@auth_router.get("/naver/login")
async def naver_login(response: Response):  # response 객체 추가
    """
    Naver OAuth 2.0 로그인 흐름을 시작합니다.
    사용자를 Naver 권한 부여 서버로 리디렉션합니다.
    state 값은 브라우저 쿠키에 저장됩니다. (Google과 동일하게 쿠키 방식으로 통일)
    """
    state = secrets.token_urlsafe(16)  # state 값 생성

    # state 값을 브라우저 쿠키에 저장 (CSRF 방지)
    response.set_cookie(
        key="oauth_state_naver",  # 네이버 전용 state 쿠키 이름 (Google과 구분)
        value=state,
        httponly=True,
        samesite="Lax",
        path="/",
        domain=None,
        # secure=True # 프로덕션 환경에서 HTTPS를 사용한다면 이 줄의 주석을 해제하세요.
    )
    print(f"DEBUG: Setting oauth_state_naver cookie with value: {state}")

    client_id = os.environ.get("NAVER_CLIENT_ID")
    redirect_uri = os.environ.get("NAVER_REDIRECT_URI")
    scope = "profile,email"  # 네이버 스코프

    auth_url_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,  # state 값을 URL 파라미터로 전달
        "scope": scope
    }
    auth_url = f"https://nid.naver.com/oauth2.0/authorize?{urlencode(auth_url_params)}"

    raise HTTPException(status_code=status.HTTP_302_FOUND, headers={"Location": auth_url})


# --- 네이버 소셜 로그인 콜백 엔드포인트 ---
@auth_router.get("/naver/callback")
async def naver_callback(
        code: str,  # Naver에서 전달하는 authorization code
        state: str,  # Naver에서 전달하는 state 값
        response: Response,
        request: Request,  # request 객체 추가
        db: Session = Depends(get_db)
):
    """
    Naver OAuth 2.0 콜백 엔드포인트.
    authorization code를 받아 access_token으로 교환하고 사용자 정보를 처리합니다.
    state 값은 브라우저 쿠키에서 검증됩니다.
    """
    # 1. state 값 검증 (CSRF 방지) - 브라우저 쿠키에서 조회
    stored_state = request.cookies.get("oauth_state_naver")  # 네이버 전용 state 쿠키 이름 사용
    print(f"DEBUG: Stored Naver state from cookie: {stored_state}, Received state from URL: {state}")

    if not stored_state or stored_state != state:
        print("DEBUG: Invalid Naver state parameter detected.")
        if not stored_state:
            print("DEBUG: 'oauth_state_naver' cookie was not found.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter"
        )

    response.delete_cookie(key="oauth_state_naver", path="/")  # 사용한 state 쿠키 삭제
    print(f"DEBUG: Naver state '{state}' validated and cookie deleted.")

    # 2. authorization_code를 access_token으로 교환
    client_id = os.environ.get("NAVER_CLIENT_ID")
    client_secret = os.environ.get("NAVER_CLIENT_SECRET")
    redirect_uri = os.environ.get("NAVER_REDIRECT_URI")

    token_url = "https://nid.naver.com/oauth2.0/token"
    token_params = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "state": state,
        "redirect_uri": redirect_uri  # 네이버는 토큰 요청 시에도 redirect_uri가 필요합니다.
    }

    try:
        async with httpx.AsyncClient() as client:
            token_res = await client.post(token_url, data=token_params)
            token_res.raise_for_status()
            token_data = token_res.json()
    except httpx.HTTPStatusError as e:
        print(f"Error getting token from Naver: {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to exchange code for token: {e.response.text}"
        )
    except httpx.RequestError as e:
        print(f"Network error during token exchange: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Network error during token exchange with Naver"
        )

    access_token = token_data.get("access_token")

    if not access_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Failed to get access token from Naver response")

    # 3. access_token으로 사용자 프로필 정보 요청
    userinfo_url = "https://openapi.naver.com/v1/nid/me"
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        async with httpx.AsyncClient() as client:
            userinfo_res = await client.get(userinfo_url, headers=headers)
            userinfo_res.raise_for_status()
            user_profile = userinfo_res.json()
    except httpx.HTTPStatusError as e:
        print(f"Error getting user info from Naver: {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to get user info from Naver: {e.response.text}"
        )
    except httpx.RequestError as e:
        print(f"Network error during user info request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Network error during user info request with Naver"
        )

    # 네이버 사용자 프로필에서 이메일과 이름 추출
    naver_response = user_profile.get("response", {})
    user_email = naver_response.get("email")
    user_name = naver_response.get("name", user_email)

    if not user_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not retrieve user email from Naver")

    # 4. 우리 서비스에 사용자 가입 또는 로그인 처리
    db_user = get_user_by_email(db, email=user_email)
    if not db_user:
        new_user_data = {
            "email": user_email,
            "name": user_name,
            "password": get_password_hash(secrets.token_urlsafe(32)),
        }
        user_create_schema = UserCreate(**new_user_data)
        db_user = create_user(db=db, user_in=user_create_schema)

    # 5. 우리 서비스의 JWT 토큰 발급 및 쿠키 설정
    our_access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    our_access_token = create_access_token(
        data={"sub": db_user.email},
        expires_delta=our_access_token_expires,
    )
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=our_access_token,
        httponly=True,
        samesite="Lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        domain=None,
    )

    # 6. 프론트엔드로 리디렉션 (로그인 성공 페이지 등)
    frontend_redirect_url = os.environ.get("APP_FRONTEND_URL", "/")
    raise HTTPException(status_code=status.HTTP_302_FOUND, headers={"Location": frontend_redirect_url})

