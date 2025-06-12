from fastapi import APIRouter
from app.features.auth.router import auth_router

router = APIRouter()

router.include_router(auth_router, prefix="/user", tags=["user"])
