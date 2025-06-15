# app/schemas/diary.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas import tags
from app.schemas.tags import TagResponse


# 일기 생성을 위한 스키마 (클라이언트 -> 서버)
class DiaryCreate(BaseModel):
    content: str = Field(
        ...,
        example="오늘은 날씨가 좋았다. 새로운 FastAPI 프로젝트를 시작했다.",
        description="일기 내용",
    )
    emotion_summary: Optional[str] = Field(
        None, example="기쁨, 만족", description="일기 요약 감정 (선택 사항)"
    )
    mood: Optional[str] = Field(
        None,
        example="기쁨",
        description="오늘의 기분 (기쁨, 슬픔, 분노, 피곤, 짜증, 무난 중 하나)",
    )

    tags: Optional[List[str]] = Field(
        default_factory=list,
        example=["행복", "개발", "일상"],
        description="일기에 연결할 태그 이름 리스트 (선택 사항)",
    )


# 일기 응답을 위한 스키마 (서버 -> 클라이언트)
class DiaryResponse(BaseModel):
    diary_id: int = Field(..., example=1, description="일기 고유 ID")
    user_id: int = Field(
        ..., example=1, description="일기 소유자 ID"
    )  # owner_id 대신 user_id 사용
    content: str = Field(
        ...,
        example="오늘은 날씨가 좋았다. 새로운 FastAPI 프로젝트를 시작했다.",
        description="일기 내용",
    )
    emotion_summary: Optional[str] = Field(
        None, example="기쁨, 만족", description="일기 요약 감정"
    )
    mood: Optional[str] = Field(None, example="기쁨", description="오늘의 기분")
    created_at: datetime = Field(
        ..., example="2025-06-11T10:00:00Z", description="일기 생성 시각"
    )
    updated_at: datetime = Field(
        ..., example="2025-06-11T10:00:00Z", description="일기 마지막 업데이트 시각"
    )
    tags: List[TagResponse] = Field(
        default_factory=list, description="연결된 태그 리스트"
    )

    class Config:
        from_attributes = True  # Pydantic v2: ORM 모드 활성화 (ORM 객체 매핑용)


# 일기 부분 업데이트를 위한 스키마 (클라이언트 -> 서버, PATCH 요청용)
class DiaryUpdate(BaseModel):
    content: Optional[str] = Field(
        None,
        example="수정된 일기 내용입니다.",
        description="수정할 일기 내용 (선택 사항)",
    )
    emotion_summary: Optional[str] = Field(
        None, example="슬픔", description="수정할 감정 요약 (선택 사항)"
    )
    mood: Optional[str] = Field(
        None, example="슬픔", description="수정할 기분 (선택 사항)"
    )

    tags: Optional[List[str]] = Field(
        None,
        example=["슬픔", "생각"],
        description="수정할 태그 이름 리스트 (선택 사항)",
    )
