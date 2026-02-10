from fastapi import FastAPI

from app.logger import get_logger

log = get_logger(__name__)
app = FastAPI(title="multi-t-inventory API", version="0.1.0")

@app.get("/")
def root():
    return {"message": "multi-t-inventory API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
