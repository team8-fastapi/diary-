from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.features.user.service import get_me, update_me, delete_me
from app.core.deps import get_db, get_current_user
from app.features.user.schemas import UserResponse, UserUpdate

user_router = APIRouter()


# 내정보 조회
@user_router.get("/me", response_model=UserResponse)
async def me(current_user: UserResponse = Depends(get_current_user)):
    return get_me(current_user)


# 내정보 수정
@user_router.patch("/me", response_model=UserResponse)
async def update(
    user_in: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_me(user_in, current_user, db)


# 회원탈퇴
@user_router.delete("/me")
async def delete(
    response: Response,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return delete_me(response, current_user, db)
