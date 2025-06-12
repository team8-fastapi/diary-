from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class MoodEnum(str, Enum):
    기쁨 = "기쁨"
    슬픔 = "슬픔"
    분노 = "분노"
    피곤 = "피곤"
    짜증 = "짜증"
    무난 = "무난"

class DiaryBase(BaseModel):
    content: str
    emotion_summary: str
    mood: MoodEnum

class DiaryCreate(DiaryBase):
    pass

class DiaryUpdate(BaseModel):
    content: str | None = None
    emotion_summary: str | None = None
    mood: MoodEnum | None = None

class DiaryOut(DiaryBase):
    diary_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True