# app/crud/user.py

from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from datetime import datetime
from typing import Optional

from app.models.user import User as UserORM, User  # SQLAlchemy ORM 모델 임포트
from app.schemas.user import UserUpdate  # Pydantic 스키마 임포트
from app.core.security import get_password_hash  # 비밀번호 해싱 유틸리티 임포트


def get_user(db: Session, user_id: int) -> Optional[UserORM]:
    """
    ID로 특정 사용자 정보를 조회합니다.
    """
    return db.execute(
        select(UserORM).filter(UserORM.user_id == user_id)
    ).scalar_one_or_none()


def get_user_by_email(db: Session, email: str) -> Optional[UserORM]:
    """
    이메일로 특정 사용자 정보를 조회합니다.
    """
    return db.execute(
        select(UserORM).filter(UserORM.email == email)
    ).scalar_one_or_none()


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
    db.refresh(db_user)  # DB에 저장된 최신 상태(예: autoincrement된 user_id)를 반영
    return db_user


def update_user(db: Session, db_user: User, user_in: UserUpdate) -> User:
    """
    기존 사용자 정보를 업데이트합니다.
    db_user: 데이터베이스에서 조회된 사용자 ORM 객체
    user_in: 클라이언트로부터 받은 업데이트될 데이터 (Pydantic UserUpdate 모델)
    """
    # Pydantic v2: .model_dump(exclude_unset=True) 사용 (기본값)
    # Pydantic v1: .dict(exclude_unset=True) 사용
    # 현재 auth.py에서 .dict()를 사용하므로 여기도 .dict()로 통일
    update_data = user_in.dict(exclude_unset=True)
    # 만약 Pydantic v2를 사용한다면:
    # update_data = user_in.model_dump(exclude_unset=True)

    # 비밀번호가 포함되어 있다면 해싱하여 업데이트
    if "password" in update_data and update_data["password"]:
        update_data["password"] = get_password_hash(update_data["password"])

    # User ORM 객체의 속성을 업데이트합니다.
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)  # 변경 사항을 세션에 추가
    db.commit()  # 데이터베이스에 커밋
    db.refresh(db_user)  # 최신 상태로 새로고침
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
