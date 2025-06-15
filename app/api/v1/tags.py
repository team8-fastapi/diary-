# app/api/v1/tags.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.tags import Tag, TagCreate
from app.models.user import Tag as TagModel
from app.deps import get_db
from app.crud.tags import get_or_create_tag
from app.deps import get_db, get_current_user
from app.schemas.user import UserResponse

tag_router = APIRouter(prefix="/tags", tags=["tags"])


# 태그 생성
@tag_router.post("/", response_model=Tag, status_code=status.HTTP_201_CREATED)
async def create_tag(
        tag_in: TagCreate,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user),
):
    tag = get_or_create_tag(db, tag_in.tags_name)
    return tag


# 태그 전체 조회
@tag_router.get("/", response_model=List[Tag])
async def read_tags(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user),
):
    tags = db.query(TagModel).offset(skip).limit(limit).all()
    return tags


# 태그 개별 조회
@tag_router.get("/{tag_id}", response_model=Tag)
async def read_tag(
        tag_id: int,
        db: Session = Depends(get_db),
):
    tag = db.query(TagModel).filter(TagModel.tags_id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


# 태그 수정
@tag_router.put("/{tag_id}", response_model=Tag)
async def update_tag(
        tag_id: int,
        tag_in: TagCreate,  # or create a separate TagUpdate schema
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user),
):
    tag = db.query(TagModel).filter(TagModel.tags_id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    tag.tags_name = tag_in.tags_name
    db.commit()
    db.refresh(tag)
    return tag


# 태그 삭제
@tag_router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
        tag_id: int,
        db: Session = Depends(get_db),
):
    tag = db.query(TagModel).filter(TagModel.tags_id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.commit()
    # 메시지 없이 그냥 종료 (204 No Content는 본문 없이 응답)
    return
