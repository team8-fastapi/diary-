# 추후 다시 새로운 패키지 디렉토리 models.py에 들어갈 것들
"""
from app.orm import Base
from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
)
from datetime import datetime

class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Diary(Base, TimestampMixin):
    __tablename__ = "diary"

    diary_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    content = Column(Text)
    emotion_summary = Column(Text)
    mood = Column(
        Enum("기쁨", "슬픔", "분노", "피곤", "짜증", "무난", name="mood_enum")
    )


class Tag(Base):
    __tablename__ = "tags"
    tags_id = Column(Integer, primary_key=True)
    tags_name = Column(String(60), nullable=False)


class DiaryTag(Base):
    __tablename__ = "diary_tags"
    diary_tag_id = Column(Integer, primary_key=True)
    diary_id = Column(Integer, ForeignKey("diary.diary_id"))
    tags_id = Column(Integer, ForeignKey("tags.tags_id"))
"""
