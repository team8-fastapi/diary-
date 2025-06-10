from fastapi import FastAPI
from app.routers import auth, user
from app.database import Base, engine


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)
