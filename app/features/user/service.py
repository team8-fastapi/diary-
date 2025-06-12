from fastapi import HTTPException, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.features.auth.repository import get_user_by_email
from app.features.user.repository import update_user, delete_user
from app.features.user.schemas import UserResponse, UserUpdate


# 내정보 조회
def get_me(current_user: UserResponse):
    return current_user


# 내정보 수정
def update_me(user_in: UserUpdate, current_user: UserResponse, db: Session):
    user = get_user_by_email(db, current_user.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return update_user(db, user, user_in)


# 회원탈퇴
def delete_me(response: Response, current_user: UserResponse, db: Session):
    deleted = delete_user(db, user_id=current_user.user_id)
    if not deleted:
        raise HTTPException(
            status_code=404, detail="User not found or could not be deleted"
        )
    response.delete_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        httponly=True,
        samesite="Lax",
        path="/",
        domain="127.0.0.1",
    )
    return {"message": "Deleted successfully"}
