from sqlalchemy import Column, String, Integer, DateTime, Boolean
from datetime import datetime
from app.database import Base


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
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)