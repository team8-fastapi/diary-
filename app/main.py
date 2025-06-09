from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()   # .env 파일 읽어서 환경변수로 로드

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}