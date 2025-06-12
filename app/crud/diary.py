from sqlalchemy.orm import Session
from app.models.user import Diary
from app.schemas.diary import DiaryCreate, DiaryUpdate, MoodEnum
from sqlalchemy import asc, desc

def create_diary(db: Session, diary_in: DiaryCreate, user_id: int) -> Diary:
    db_diary = Diary(**diary_in.dict(), user_id=user_id)
    db.add(db_diary)
    db.commit()
    db.refresh(db_diary)
    return db_diary

def get_diary(db: Session, diary_id: int, user_id: int) -> Diary | None:
    return db.query(Diary).filter_by(diary_id=diary_id, user_id=user_id).first()


def get_diaries(db: Session, user_id: int, skip: int = 0, limit: int = 10,
                mood: MoodEnum | None = None,
                order_by: str | None = None):
    query = db.query(Diary).filter(Diary.user_id == user_id)

    # 검색 (예: mood)를 통한 필터
    if mood:
        query = query.filter(Diary.mood == mood)

    # 정렬 기능
    if order_by:
        desc_flag = order_by.startswith('-')
        field = order_by.lstrip('+-')
        col = getattr(Diary, field, None)
        if col is not None:
            query = query.order_by(desc(col) if desc_flag else asc(col))

    # 페이징
    return query.offset(skip).limit(limit).all()

def update_diary(db: Session, diary_id: int, user_id: int, diary_up: DiaryUpdate) -> Diary:
    db_diary = get_diary(db, diary_id, user_id)
    if not db_diary:
        return None
    for field, value in diary_up.dict(exclude_unset=True).items():
        setattr(db_diary, field, value)
    db.commit()
    db.refresh(db_diary)
    return db_diary

def delete_diary(db: Session, diary_id: int, user_id: int) -> bool:
    db_diary = get_diary(db, diary_id, user_id)
    if not db_diary:
        return False
    db.delete(db_diary)
    db.commit()
    return True
