# app/crud/tags.py
from sqlalchemy.orm import Session
from app.models.user import Tag, Diarytag
from typing import List
from app.schemas.tags import TagCreate



# 태그 생성
def get_or_create_tag(db: Session, tag_name: str) -> Tag:
    tag = db.query(Tag).filter(Tag.tags_name == tag_name).first()
    if tag is None:
        tag = Tag(tags_name=tag_name)
        db.add(tag)
        db.commit()
        db.refresh(tag)
    return tag


# 태그 연결
def attach_tags_to_diary(db: Session, diary_id: int, tags: List[TagCreate]):
    for tag_data in tags:
        tag = get_or_create_tag(db, tag_data.tags_name)
        diary_tag = Diarytag(diary_id=diary_id, tags_id=tag.tags_id)
        db.add(diary_tag)
    db.commit()


# 태그 수정
def update_tags_of_diary(db: Session, diary_id: int, tags: List[TagCreate]):
    db.query(Diarytag).filter(Diarytag.diary_id == diary_id).delete()
    db.commit()
    attach_tags_to_diary(db, diary_id, tags)


# 태그 삭제
def delete_tags_by_diary_id(db: Session, diary_id: int):
    db.query(Diarytag).filter(Diarytag.diary_id == diary_id).delete()
    db.commit()