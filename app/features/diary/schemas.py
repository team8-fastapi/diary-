from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# 일기 생성용 스키마 (요청)
class DiaryCreate(BaseModel):
    content: str = Field(..., example="오늘은 날씨가 좋았다.", description="일기 내용")
    emotion_summary: Optional[str] = Field(
        None, example="기쁨, 만족", description="감정 요약"
    )
    mood: Optional[str] = Field(None, example="기쁨", description="오늘의 기분")


# 일기 응답용 스키마 (응답)
class DiaryResponse(BaseModel):
    diary_id: int
    user_id: int
    content: str
    emotion_summary: Optional[str]
    mood: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
