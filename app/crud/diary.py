# app/crud/diary.py
from sqlalchemy.orm import Session
from app.models.user import (
    Diary,
    Tag,
)  # app.models.diary 대신 app.models.user에서 Diary 임포트
from app.schemas.diary import DiaryCreate, DiaryUpdate
from typing import List, Optional
from sqlalchemy import delete, or_, asc, desc
from app.crud import tags


def create_diary(db: Session, diary: DiaryCreate, user_id: int) -> Diary:
    """
    새로운 일기 항목을 생성합니다.
    """
    diary_data = diary.dict(exclude={"tags"})
    db_diary = Diary(**diary_data, user_id=user_id)
    db.add(db_diary)
    db.commit()
    db.refresh(db_diary)

    # tags 태그 연결
    if diary.tags:
        tags.attach_tags_to_diary(db, db_diary, diary.tags)

    return db_diary


def get_diaries(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc",
) -> List[Diary]:
    """
    특정 사용자의 모든 일기 항목을 조회합니다.
    """

    query = db.query(Diary).filter(Diary.user_id == user_id)

    if search:
        query = query.filter(
            or_(
                Diary.content.ilike(f"%{search}%"),
                Diary.emotion_summary.ilike(f"%{search}%"),
            )
        )

        # 정렬 기능
    if sort_by and hasattr(Diary, sort_by):
        order_func = asc if sort_order.lower() == "asc" else desc
        query = query.order_by(order_func(getattr(Diary, sort_by)))

        # 페이징
    diaries = query.offset(skip).limit(limit).all()
    return diaries


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
    # 일기 내용 수정
    if diary_update.content is not None:
        db_diary.content = diary_update.content

    if diary_update.emotion_summary is not None:
        db_diary.emotion_summary = diary_update.emotion_summary

    if diary_update.mood is not None:
        db_diary.mood = diary_update.mood

    # 태그 수정
    if diary_update.tags is not None:
        tag_objs = []
        for tag_name in diary_update.tags:
            tag = db.query(Tag).filter_by(tags_name=tag_name).first()
            if not tag:
                tag = Tag(tags_name=tag_name)
                db.add(tag)
                db.flush()  # ID 생성
            tag_objs.append(tag)
        db_diary.tags = tag_objs
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
