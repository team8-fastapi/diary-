# app/main.py
from fastapi import FastAPI
from app.api.v1.auth import auth_router

# from app.api.v1.users import users_router # 다른 라우터도 추가 가능

app = FastAPI()

app.include_router(auth_router)
# app.include_router(users_router, prefix="/api/v1") # API 버전 접두사 추가
