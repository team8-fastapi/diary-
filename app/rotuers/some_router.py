from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()

@router.get("/ping")
def ping(db: Session = Depends(get_db)):
    return {"message": "pong"}
