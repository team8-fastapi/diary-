from sqlalchemy import Column, Integer, DateTime, Text, Enum, ForeignKey
from datetime import datetime
from app.database import Base

class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Diary(Base, TimestampMixin):
    __tablename__ = "diary"

    diary_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user.id"))
    content = Column(Text)
    emotion_summary = Column(Text)
    mood = Column(Enum("기쁨", "슬픔", "분노", "피곤", "짜증", "무난", name="mood_enum"))



