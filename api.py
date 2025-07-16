from fastapi import FastAPI
import uvicorn

app = FastAPI(title="ForestBytes Catalog API", version="1.0.0")


@app.get("/")
def health():
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
