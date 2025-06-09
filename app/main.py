from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def main():
    return "Hello from team8-fastapi!"


if __name__ == "__main__":
    main()
