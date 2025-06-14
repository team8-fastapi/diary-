# app/crud/diary.py
from sqlalchemy.orm import Session
from app.models.user import (
    Diary,
)  # app.models.diary 대신 app.models.user에서 Diary 임포트
from app.schemas.diary import DiaryCreate, DiaryUpdate
from typing import List, Optional
from sqlalchemy import delete
from app.crud import tags


def create_diary(db: Session, diary: DiaryCreate, user_id: int) -> Diary:
    """
    새로운 일기 항목을 생성합니다.
    """
    db_diary = Diary(**diary.dict(), user_id=user_id)  # Pydantic v1의 .dict() 사용
    # Pydantic v2라면 db_diary = Diary(**diary.model_dump(), user_id=user_id)
    db.add(db_diary)
    db.commit()
    db.refresh(db_diary)
    return db_diary


def get_diaries(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[Diary]:
    """
    특정 사용자의 모든 일기 항목을 조회합니다.
    """
    return (
        db.query(Diary).filter(Diary.user_id == user_id).offset(skip).limit(limit).all()
    )


def get_diary_by_id(db: Session, diary_id: int, user_id: int) -> Optional[Diary]:
    """
    특정 일기 항목을 ID로 조회합니다. (소유자 확인 포함)
    """
    return (
        db.query(Diary)
        .filter(Diary.diary_id == diary_id, Diary.user_id == user_id)
        .first()
    )


def update_diary(db: Session, db_diary: Diary, diary_update: DiaryUpdate) -> Diary:
    """
    일기 항목을 업데이트합니다.
    """
    update_data = diary_update.dict(exclude_unset=True)  # Pydantic v1의 .dict() 사용
    # Pydantic v2라면 update_data = diary_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_diary, key, value)

    db.add(db_diary)
    db.commit()
    db.refresh(db_diary)
    return db_diary


def delete_diary(db: Session, diary_id: int, user_id: int) -> bool:
    """
    일기 항목을 삭제합니다. (소유자 확인 포함)
    """
    stmt = delete(Diary).where(Diary.diary_id == diary_id, Diary.user_id == user_id)
    result = db.execute(stmt)
    db.commit()
    return result.rowcount > 0
