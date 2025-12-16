from io import BytesIO, StringIO
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pipeline import run_pipeline_on_dataframe
from app.services.etl_state import etl_state_manager
from typing import Any
import pandas as pd
import numpy as np

router = APIRouter()


def convert_to_json_serializable(obj: Any) -> Any:
    """
    Convierte tipos numpy a tipos nativos de Python para serialización JSON.

    Contexto:
    - FastAPI/Pydantic no puede serializar directamente numpy.int64, numpy.float64, etc.

    Para qué:
    - Evitar errores de serialización cuando devolvemos summaries del pipeline.
    """
    if isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_to_json_serializable(item) for item in obj)
    elif isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    else:
        return obj

def json_safe(obj: Any) -> Any:
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        val = float(obj)
        return None if np.isnan(val) else val
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, dict):
        return {str(k): json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [json_safe(x) for x in obj]
    return obj

@router.post("/run")
async def run_pipeline(file: UploadFile = File(...)):
    """
    Process uploaded file (CSV or Excel) and run ETL pipeline.
    Accepts .csv, .xlsx, .xls files.
    """
    try:
        content_bytes = await file.read()
        filename = file.filename.lower()

        # Detect file type and read accordingly
        if filename.endswith('.csv'):
            content_str = content_bytes.decode("utf-8")
            df_raw = pd.read_csv(StringIO(content_str), header=None)
        elif filename.endswith(('.xlsx', '.xls')):
            df_raw = pd.read_excel(BytesIO(content_bytes), header=None)
        else:
            raise HTTPException(
                status_code=400,
                detail="Formato de archivo no soportado. Use .csv, .xlsx o .xls"
            )

        # Run the pipeline
        _, summary = run_pipeline_on_dataframe(df_raw)
        return json_safe(summary)

    except HTTPException:
        raise
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Error al decodificar el archivo. Asegúrese de que sea un archivo válido."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el archivo: {str(e)}"
        )

@router.get("/status")
async def get_pipeline_status():
    """Get current ETL pipeline status"""
    return etl_state_manager.get_state()

@router.post("/reset")
async def reset_pipeline_status():
    """Reset ETL pipeline status to idle"""
    etl_state_manager.reset()
    return {"message": "Pipeline status reset successfully"}

