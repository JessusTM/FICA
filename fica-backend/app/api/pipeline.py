from io import StringIO
from fastapi import APIRouter, UploadFile, File
from app.services.pipeline import run_pipeline_on_dataframe
import pandas as pd

router = APIRouter()

@router.post("/run")
async def run_pipeline(file: UploadFile = File(...)):
    content_bytes = await file.read()
    content_str   = content_bytes.decode("utf-8")
    df_raw        = pd.read_csv(StringIO(content_str), header=None)
    _, summary    = run_pipeline_on_dataframe(df_raw)
    return summary
