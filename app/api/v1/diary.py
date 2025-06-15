# app/api/v1/diary.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.schemas.diary import (
    DiaryCreate,
    DiaryResponse,
    DiaryUpdate,
)  # 일기 스키마 임포트
from app.crud import diary as crud_diary  # 일기 CRUD 함수 임포트 (별칭 사용)
from app.deps import get_db, get_current_user  # DB 세션 및 현재 사용자 의존성 임포트
from app.schemas.user import UserResponse  # 현재 사용자 타입 힌트용

diary_router = APIRouter(prefix="/diary", tags=["Diary"])

# 다이어리 생성
@diary_router.post(
    "/", response_model=DiaryResponse, status_code=status.HTTP_201_CREATED
)
async def create_new_diary(
    diary_in: DiaryCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    새로운 일기 항목을 생성합니다. (라우터)
    """
    return crud_diary.create_diary(db=db, diary=diary_in, user_id=current_user.user_id)

# 다이어리 조회
@diary_router.get("/", response_model=List[DiaryResponse])
async def read_diaries(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc",
):
    """
    현재 로그인된 사용자의 모든 일기 항목을 조회합니다. (라우터)
    """
    diaries = crud_diary.get_diaries(
        db=db,
        user_id=current_user.user_id,
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return [DiaryResponse.model_validate(d, from_attributes=True) for d in diaries]


@diary_router.get("/{diary_id}", response_model=DiaryResponse)
async def read_diary_by_id(
    diary_id: int,  # 경로 매개변수 diary_id
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    특정 ID의 일기 항목을 조회합니다. (소유자만 접근 가능) (라우터)
    """
    diary = crud_diary.get_diary_by_id(
        db=db, diary_id=diary_id, user_id=current_user.user_id
    )
    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Diary not found"
        )
    return diary


@diary_router.patch("/{diary_id}", response_model=DiaryResponse)
async def update_existing_diary(
    diary_id: int,  # 경로 매개변수 diary_id
    diary_update: DiaryUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    특정 ID의 일기 항목을 업데이트합니다. (소유자만 수정 가능) (라우터)
    """
    db_diary = crud_diary.get_diary_by_id(
        db=db, diary_id=diary_id, user_id=current_user.user_id
    )
    if not db_diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Diary not found"
        )

    updated_diary = crud_diary.update_diary(
        db=db, db_diary=db_diary, diary_update=diary_update
    )
    return updated_diary


@diary_router.delete(
    "/{diary_id}", status_code=status.HTTP_200_OK
)  # 메시지 반환을 위해 200 OK로 변경
async def delete_existing_diary(
    diary_id: int,  # 경로 매개변수 diary_id
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    특정 ID의 일기 항목을 삭제합니다. (소유자만 삭제 가능) (라우터)
    """
    diary_deleted = crud_diary.delete_diary(
        db=db, diary_id=diary_id, user_id=current_user.user_id
    )
    if not diary_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diary not found or could not be deleted",
        )
    return {"message": "일기가 성공적으로 삭제되었습니다."}  # 삭제 메시지 반환
