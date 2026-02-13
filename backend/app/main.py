from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.logger import get_logger
from app.api.v1.api import api_router

log = get_logger(__name__)
app = FastAPI(title="multi-t-inventory API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
