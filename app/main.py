# app/main.py
from fastapi import FastAPI, Request
from app.api.v1.diary import router
from app.api.v1.auth import auth_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# from app.api.v1.users import users_router # 다른 라우터도 추가 가능

app = FastAPI()

app.include_router(auth_router)
app.include_router(router)
# app.include_router(users_router, prefix="/api/v1") # API 버전 접두사 추가

app.mount("/static", StaticFiles(directory="app/frontend"), name="static")

@app.get("/auth/signup", response_class=HTMLResponse)
def get_signup_page():
    with open("app/frontend/user/signup.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/auth/login", response_class=HTMLResponse)
def login_page():
    with open("app/frontend/user/login.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/auth/me-page", response_class=HTMLResponse)
async def me_page():
    with open("app/frontend/user/me.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/auth/logout", response_class=HTMLResponse)
def logout_page():
    with open("app/frontend/user/logout.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/delete", response_class=HTMLResponse)
async def delete_page():
    with open("app/frontend/user/delete.html") as f:
        return f.read()

@app.get("/diaries/create", response_class=HTMLResponse)
async def get_create_page():
    with open("app/frontend/diary/create_diary.html", encoding="utf-8") as f:
        return f.read()

@app.get("/diaries/list", response_class=HTMLResponse)
async def get_list_page():
    with open("app/frontend/diary/diary_list.html", encoding="utf-8") as f:
        return f.read()

@app.get("/diaries/update", response_class=HTMLResponse)
async def get_update_page():
    with open("app/frontend/diary/diary_update.html", encoding="utf-8") as f:
        return f.read()

@app.get("/diaries/delete", response_class=HTMLResponse)
async def get_delete_page():
    with open("app/frontend/diary/diary_delete.html", encoding="utf-8") as f:
        return f.read()

@app.get("/", response_class=HTMLResponse)
async def get_main_page():
    with open("app/frontend/main.html", encoding="utf-8") as f:
        return f.read()

