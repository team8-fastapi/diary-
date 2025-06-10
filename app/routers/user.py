from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.schemas.auth import UserUpdate, UserOut
from app.services.auth import get_user_by_email, update_user, delete_user
from app.database import get_db
from app.core.security import decode_token


router = APIRouter(prefix="/user", tags=["user"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = "your_super_secret_key"
ALGORITHM = "HS256"


def get_current_user_email(token: str = Depends(oauth2_scheme)) -> str:
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    return email


@router.get("/me", response_model=UserOut)
def read_current_user(
    current_email: str = Depends(get_current_user_email), db: Session = Depends(get_db)
):
    user = get_user_by_email(db, current_email)
    return user


@router.patch("/me", response_model=UserOut)
def patch_current_user(
    user_update: UserUpdate,
    current_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
):
    updated_user = update_user(db, current_email, user_update)
    return updated_user


@router.delete("/me")
def remove_current_user(
    current_email: str = Depends(get_current_user_email), db: Session = Depends(get_db)
):
    delete_user(db, current_email)
    return {"msg": "Deleted successfully"}
