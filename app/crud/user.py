# app/crud/user.py

from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from datetime import datetime
from typing import Optional

from app.models.user import User as UserORM # SQLAlchemy ORM 모델 임포트
from app.schemas.user import UserCreate, UserUpdate # Pydantic 스키마 임포트
from app.core.security import get_password_hash # 비밀번호 해싱 유틸리티 임포트


def get_user(db: Session, user_id: int) -> Optional[UserORM]:
    """
    ID로 특정 사용자 정보를 조회합니다.
    """
    return db.execute(select(UserORM).filter(UserORM.user_id == user_id)).scalar_one_or_none()

def get_user_by_email(db: Session, email: str) -> Optional[UserORM]:
    """
    이메일로 특정 사용자 정보를 조회합니다.
    """
    return db.execute(select(UserORM).filter(UserORM.email == email)).scalar_one_or_none()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[UserORM]:
    """
    모든 사용자 목록을 조회합니다.
    """
    return db.execute(select(UserORM).offset(skip).limit(limit)).scalars().all()

def create_user(db: Session, user_data: dict) -> UserORM:
    """
    새로운 사용자를 생성합니다.
    user_data는 이미 해싱된 비밀번호를 포함한 dict 형태여야 합니다.
    """
    # user_data에서 password는 이미 해싱되어 있다고 가정
    db_user = UserORM(**user_data)
    db_user.created_at = datetime.utcnow()
    db_user.updated_at = datetime.utcnow()

    db.add(db_user)
    db.commit()
    db.refresh(db_user) # DB에 저장된 최신 상태(예: autoincrement된 user_id)를 반영
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[UserORM]:
    """
    특정 사용자 정보를 업데이트합니다.
    """
    # 먼저 사용자 존재 여부 확인
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    # Pydantic 모델의 업데이트 데이터를 딕셔너리로 변환하고 None이 아닌 값만 필터링
    update_data = user_update.model_dump(exclude_unset=True) # Pydantic v2
    # update_data = user_update.dict(exclude_unset=True) # Pydantic v1

    # 비밀번호가 있다면 해싱하여 업데이트 데이터에 반영
    if "password" in update_data and update_data["password"]:
        update_data["password"] = get_password_hash(update_data["password"])

    # SQLAlchemy 2.0 스타일로 UPDATE 쿼리 실행
    stmt = (
        update(UserORM)
        .where(UserORM.user_id == user_id)
        .values(**update_data, updated_at=datetime.utcnow()) # updated_at 자동 업데이트
    )
    db.execute(stmt)
    db.commit()

    # 업데이트된 사용자 객체를 다시 조회하여 반환
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """
    특정 사용자를 삭제합니다.
    """
    stmt = delete(UserORM).where(UserORM.user_id == user_id)
    result = db.execute(stmt)
    db.commit()
    # 삭제된 행이 있는지 확인 (rowcount > 0)
    return result.rowcount > 0

# (선택) 사용자 마지막 로그인 시간 업데이트 함수
def update_last_login(db: Session, user_id: int):
    """
    사용자의 마지막 로그인 시간을 현재 시각으로 업데이트합니다.
    """
    stmt = (
        update(UserORM)
        .where(UserORM.user_id == user_id)
        .values(last_login=datetime.utcnow())
    )
    db.execute(stmt)
    db.commit()