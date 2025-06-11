from app.orm import Base
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from zoneinfo import ZoneInfo


def kstnow():
    return datetime.now(ZoneInfo("Asia/Seoul"))


class TimestampMixin:
    created_at = Column(DateTime, default=kstnow)
    updated_at = Column(DateTime, default=kstnow, onupdate=kstnow)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    full_name = Column(String(20), nullable=False)
    username = Column(String(20), nullable=False)
    phone_number = Column(String(20), nullable=True)
    last_login = Column(DateTime)
    is_staff = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    refresh_tokens = relationship("RefreshToken", back_populates="user")


# refresh 토큰 테이블 추가
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(256), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="refresh_tokens")
