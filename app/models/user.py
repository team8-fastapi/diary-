from sqlalchemy import Column, String, Integer, DateTime, Boolean
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
class User(Base, TimestampMixin):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(20), nullable=False)
    phone_number = Column(String(15), nullable=True)
    last_login = Column(DateTime)
    is_staff = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)