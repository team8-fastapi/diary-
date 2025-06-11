from fastapi import FastAPI
from app.api.v1.router import router as all_router

app = FastAPI()

app.include_router(all_router, prefix="/api/v1")
