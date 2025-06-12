from sqlalchemy.orm import Session
from app.features.user.models import Diary
from app.features.diary.schemas import DiaryCreate


def create_diary(db: Session, diary: DiaryCreate, user_id: int) -> Diary:
    """
    새로운 일기 항목을 DB에 저장합니다.
    """
    db_diary = Diary(**diary.dict(), user_id=user_id)
    db.add(db_diary)
    db.commit()
    db.refresh(db_diary)
    return db_diary
