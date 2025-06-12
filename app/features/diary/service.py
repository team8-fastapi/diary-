from sqlalchemy.orm import Session
from app.features.diary.schemas import DiaryCreate
from app.features.user.schemas import UserResponse
from app.features.diary.repository import create_diary as repo_create_diary


def create_new_diary(user: UserResponse, diary_in: DiaryCreate, db: Session):
    """
    새로운 일기를 생성하는 비즈니스 로직
    """
    return repo_create_diary(db=db, diary=diary_in, user_id=user.user_id)
