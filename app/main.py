from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello_world_handler():
    return {"message": "Hello World178"}