from fastapi import APIRouter


router = APIRouter()

router.include_router(router, prefix="/auth", tags=["auth"])
