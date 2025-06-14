# app/api/v1/router.py
from fastapi import APIRouter

# 각 라우터 파일에서 정의된 APIRouter 인스턴스 임포트
from app.api.v1.auth import auth_router  # auth.py에서 auth_router 임포트
from app.api.v1.diary import diary_router  # diary.py에서 diary_router 임포트
from app.api.v1.tags import tag_router  # tag.py에서 diary_router 임포트

# v1 API 전체를 위한 APIRouter 인스턴스 생성
api_router = APIRouter(prefix="/v1")

# 각 개별 라우터들을 api_router에 포함
api_router.include_router(auth_router)
api_router.include_router(diary_router)
api_router.include_router(tag_router)
