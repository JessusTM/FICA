from fastapi import APIRouter
from app.core.logging import setup_logging

setup_logging()

router = APIRouter()
