import os
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import httpx  # 외부 HTTP 요청을 위한 라이브러리
from urllib.parse import urlencode  # URL 인코딩을 위해 필요
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

    # 계정 삭제 성공 후, 사용자 세션(쿠키)도 삭제
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        httponly=True,
        samesite="Lax",
        path="/",
        domain=None,
        # secure=True # 프로덕션 환경에서 HTTPS를 사용한다면 이 줄의 주석을 해제하세요.
    )
    # Refresh Token도 사용한다면 여기서 삭제 로직 추가 (블랙리스트 포함)
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


# Google 소셜 로그인 시작 엔드포인트
@auth_router.get("/google/login")
async def google_login(response: Response):
    """
    Google OAuth 2.0 로그인 흐름을 시작합니다.
    사용자를 Google 권한 부여 서버로 리디렉션합니다.
    """
    state = secrets.token_urlsafe(16)

    # state 쿠키를 설정합니다. domain 속성을 제거하여 브라우저가 자동으로 호스트 도메인을 사용하도록 합니다.
    # secure=True는 HTTP 연결에서는 쿠키 전송을 막으므로, 현재 HTTP 사용 시에는 주석 처리 유지.
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        samesite="Lax",
        path="/",
        # domain=None, # 이전에 명시된 domain 속성을 제거한 상태
        # secure=True # HTTPS 사용 시 주석 해제 (현재는 주석 처리 유지)
    )

    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI")
    scope = "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile openid"  # openid 추가 권장

    auth_url_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
        "access_type": "offline",  # refresh token을 받기 위해
        "prompt": "consent",  # 매번 동의 화면을 보여주기 위해
    }
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(auth_url_params)}"
    )

    # 사용자를 Google 인증 서버로 리디렉션합니다.
    # set_cookie 호출 이후에 HTTPException을 발생시켜야 쿠키가 포함됩니다.
    raise HTTPException(
        status_code=status.HTTP_302_FOUND, headers={"Location": auth_url}
    )


# Google 소셜 로그인 콜백 엔드포인트
@auth_router.get("/google/callback")
async def google_callback(
    code: str,  # Google에서 전달하는 authorization code
    state: str,  # Google에서 전달하는 state 값
    response: Response,
    request: Request,  # Request 객체에서 쿠키를 읽기 위해 필요
    db: Session = Depends(get_db),
):
    """
    Google OAuth 2.0 콜백 엔드포인트.
    authorization code를 받아 access_token으로 교환하고 사용자 정보를 처리합니다.
    """
    # 1. state 값 검증 (CSRF 방지)
    stored_state = request.cookies.get("oauth_state")
    if not stored_state or stored_state != state:
        # 디버깅을 위해 로그 추가
        print(f"DEBUG: Stored state: {stored_state}, Received state: {state}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter"
        )
    response.delete_cookie(key="oauth_state", path="/")  # 사용한 state 쿠키 삭제

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
        "grant_type": "authorization_code",
    }

    try:
        async with httpx.AsyncClient() as client:
            token_res = await client.post(token_url, data=token_params)
            token_res.raise_for_status()  # HTTP 오류 발생 시 예외 발생
            token_data = token_res.json()
    except httpx.HTTPStatusError as e:
        print(f"Error getting token from Google: {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,  # Google에서 받은 실제 상태 코드를 반환
            detail=f"Failed to exchange code for token: {e.response.text}",
        )
    except httpx.RequestError as e:
        print(f"Network error during token exchange: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Network error during token exchange with Google",
        )

    access_token = token_data.get("access_token")
    # refresh_token = token_data.get("refresh_token") # 필요하다면 저장

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get access token from Google response",
        )

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
            status_code=e.response.status_code,  # Google에서 받은 실제 상태 코드를 반환
            detail=f"Failed to get user info from Google: {e.response.text}",
        )
    except httpx.RequestError as e:
        print(f"Network error during user info request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Network error during user info request with Google",
        )

    user_email = user_profile.get("email")
    user_name = user_profile.get("name", user_email)  # 이름이 없으면 이메일 사용
    # profile_picture = user_profile.get("picture")

    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not retrieve user email from Google",
        )

    # 4. 우리 서비스에 사용자 가입 또는 로그인 처리
    db_user = get_user_by_email(db, email=user_email)
    if not db_user:
        # 새로운 사용자: 회원가입 (비밀번호는 임의로 생성하거나 소셜 유저임을 표시)
        new_user_data = {
            "email": user_email,
            "username": user_name,  # 소셜 계정 이름
            "password": get_password_hash(
                secrets.token_urlsafe(32)
            ),  # 임의의 강력한 비밀번호
            # "is_social_user": True # 소셜 로그인 사용자임을 표시하는 필드 (필요시 UserCreate 스키마에 추가)
        }
        # user_in 인스턴스를 생성하여 create_user 함수에 전달합니다.
        # UserCreate 스키마가 is_social_user 필드를 가진다면 여기에 추가할 수 있습니다.
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
        # secure=True # 프로덕션 환경에서 HTTPS를 사용한다면 이 줄의 주석을 해제하세요.
    )

    # 6. 프론트엔드로 리디렉션 (로그인 성공 페이지 등)
    frontend_redirect_url = os.environ.get(
        "APP_FRONTEND_URL", "/"
    )  # APP_FRONTEND_URL 환경변수 사용
    raise HTTPException(
        status_code=status.HTTP_302_FOUND, headers={"Location": frontend_redirect_url}
    )
