from fastapi import FastAPI

from app.core.config import config
from app.core.logging import setup_logging
from app.api.pipeline import router as pipeline_router
from app.api.kpi import router as kpi_router
from app.api.tables import router as tables_router  

setup_logging()
app = FastAPI()

app.include_router(
    pipeline_router,
    prefix="/api/pipeline",
    tags=["pipeline"],
)

app.include_router(
    tables_router,
    prefix="/api/tables",
    tags=["tables"],
)

app.include_router(kpi_router)
