from fastapi import APIRouter

from app.auth.router import auth_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
