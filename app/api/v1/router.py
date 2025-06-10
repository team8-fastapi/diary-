from fastapi import APIRouter

from app.features.auth import auth_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
