from fastapi import APIRouter
from app.features.auth.router import auth_router
from app.features.user.router import user_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(user_router, prefix="/user", tags=["User"])
