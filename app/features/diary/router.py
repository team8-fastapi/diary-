from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.features.diary.schemas import DiaryResponse, DiaryCreate
from app.features.diary.service import create_new_diary
from app.features.user.schemas import UserResponse

diary_router = APIRouter()


@diary_router.post(
    "/", response_model=DiaryResponse, status_code=status.HTTP_201_CREATED
)
async def create_diary(
    diary_in: DiaryCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    새로운 일기 작성 API
    """
    return create_new_diary(user=current_user, diary_in=diary_in, db=db)
