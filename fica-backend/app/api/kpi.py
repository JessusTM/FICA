from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database.db import get_db
from app.services.kpi.registry import KPI_REGISTRY

router = APIRouter(prefix="/kpi", tags=["KPI"])


@router.get("/list")
def list_kpis() -> Dict[str, Any]:
    return {
        "kpis": sorted(KPI_REGISTRY.keys())
    }


@router.get("/{kpi_id}")
def get_kpi(
    kpi_id  : str,
    cohorte : int       = Query(2022, ge=1900, le=2100),
    db      : Session   = Depends(get_db),
) -> Dict[str, Any]:
    fn = KPI_REGISTRY.get(kpi_id)
    if fn is None:
        raise HTTPException(status_code=404, detail=f"KPI '{kpi_id}' no existe")

    try:
        result = fn(db, cohorte)
        return {
            "kpi_id"    : kpi_id,
            "cohorte"   : cohorte,
            "result"    : result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando KPI {kpi_id}: {str(e)}")
