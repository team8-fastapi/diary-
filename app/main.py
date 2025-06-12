# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # CORS 미들웨어 임포트

# app/api/v1/router.py에서 정의한 api_router 임포트
from app.api.v1.router import api_router

app = FastAPI(
    title="Diary FastAPI 애플리케이션",  # 앱 제목 (한글)
    description="일기 작성 및 관리를 위한 FastAPI 애플리케이션입니다.",  # 앱 설명 (한글)
    version="0.1.0",  # 앱 버전
    docs_url="/docs",  # Swagger UI 경로
    redoc_url="/redoc",  # ReDoc 경로
)

# CORS 미들웨어 설정
# 실제 배포 시에는 allow_origins에 프론트엔드의 도메인을 명시해야 합니다.
# 개발 환경에서는 localhost 또는 개발 서버 주소를 포함합니다.
origins = [
    "http://localhost",
    "http://localhost:3000",  # React/Vue/Angular 개발 서버 주소 (예시)
    "http://127.0.0.1",  # 로컬호스트 IP (FastAPI 서버가 실행되는 주소)
    "http://127.0.0.1:8000",  # FastAPI 서버 주소
    # "https://your-frontend-domain.com", # 배포 시 프론트엔드 도메인 추가
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 허용할 오리진 (도메인) 목록
    allow_credentials=True,  # 쿠키(인증 정보)를 포함한 요청 허용 (JWT 쿠키를 위해 필수)
    allow_methods=["*"],  # 모든 HTTP 메서드 허용 (GET, POST, PUT, PATCH, DELETE 등)
    allow_headers=["*"],  # 모든 헤더 허용
)

# v1 API 라우터 포함
# 이 라우터에 포함된 모든 엔드포인트는 "/api" 접두사를 가집니다.
# 예를 들어, /v1/auth/login이 /api/v1/auth/login이 됩니다.
app.include_router(api_router, prefix="/api")


# 선택 사항: 루트 경로에 대한 기본 응답
@app.get("/")
async def root():
    return {"message": "환영합니다! FastAPI 애플리케이션이 실행 중입니다."}
