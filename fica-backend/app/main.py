from fastapi import FastAPI

from app.core.config import config
from app.core.logging import setup_logging
from app.api.pipeline import router as pipeline_router

setup_logging()

app = FastAPI()

app.include_router(
    pipeline_router,
    prefix="/api/pipeline",
    tags=["pipeline"],
)
