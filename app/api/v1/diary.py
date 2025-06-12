from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.diary import DiaryOut, DiaryCreate, DiaryUpdate
from app.crud.diary import create_diary, get_diary, get_diaries, update_diary, delete_diary
from app.deps import get_current_user, get_db

router = APIRouter(prefix="/diaries", tags=["diaries"])

@router.post("/", response_model=DiaryOut)
def create_new_diary(diary_in: DiaryCreate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return create_diary(db, diary_in, user.user_id)

@router.get("/", response_model=List[DiaryOut])
def list_diaries(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return get_diaries(db, user.user_id, skip, limit)

@router.get("/{diary_id}", response_model=DiaryOut)
def read_diary(diary_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    d = get_diary(db, diary_id, user.user_id)
    if not d:
        raise HTTPException(404, "Diary not found")
    return d

@router.patch("/{diary_id}", response_model=DiaryOut)
def patch_diary(diary_id: int, diary_up: DiaryUpdate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    d = update_diary(db, diary_id, user.user_id, diary_up)
    if not d:
        raise HTTPException(404, "Diary not found")
    return d

@router.delete("/{diary_id}", status_code=204)
def remove_diary(diary_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    ok = delete_diary(db, diary_id, user.user_id)
    if not ok:
        raise HTTPException(404, "Diary not found")
