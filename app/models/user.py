from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(16))
    password = Column(String(60))
    created_at = Column(DateTime, default=datetime.now)
