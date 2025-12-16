import pandas as pd
from sqlalchemy.engine import Engine
from typing import Any, Dict, Tuple, Optional

from app.services.etl.delete_algebra_classes import filter_out_algebra
from app.services.etl.group_by_test import group_by_test
from app.services.etl.group_by_student import group_by_student
from app.services.etl.populate_database import populate_all
from app.services.etl.build_gold import build_all_gold
from app.services.etl.populate_gold import populate_gold_all
from app.core.database.db import get_raw_connection


def run_pipeline_on_dataframe(
    df: pd.DataFrame,
    db_engine: Optional[Engine] = None,
) -> Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]]:
    """
    Ejecuta el pipeline ETL completo sobre un DataFrame (Bronze/Silver en memoria) y persiste en DB.

    Contexto:
    - Este pipeline toma el DataFrame original (entrada), aplica transformaciones Silver,
      carga el modelo base en PostgreSQL (populate_all) y luego construye + persiste tablas Gold
      para simplificar los KPIs.

    Para qué:
    - Dejar lista la BD con:
      1) Tablas base (estudiantes, rendimiento, paes/pdt, etc.)
      2) Tablas Gold (gold_kpi_*) para evitar joins/cálculos repetidos en cada KPI

    Dónde se usa:
    - Servicio principal de procesamiento al cargar un CSV (o data equivalente) en el sistema.
    """
    # ------ Copia de entrada ------
    dataframe_input = df.copy()

    # ------ Silver: filtrado/ordenamiento/normalización ------
    dataframe_filtered, summary_filter                      = filter_out_algebra(dataframe_input)
    dataframe_grouped_test, summary_group_test              = group_by_test(dataframe_filtered)
    dataframe_silver_student_rows, summary_group_student    = group_by_student(dataframe_grouped_test)

    # ------ Gold: construir tablas en memoria (desde df Silver final) ------
    gold_tables_by_name = build_all_gold(dataframe_silver_student_rows)

    # ------ Persistencia: Base + Gold en DB ------
    if db_engine is None:
        with get_raw_connection() as connection:
            summary_database_base = populate_all(connection, dataframe_silver_student_rows)
            summary_database_gold = populate_gold_all(connection, gold_tables_by_name)
    else:
        connection = db_engine.raw_connection()
        try:
            summary_database_base = populate_all(connection, dataframe_silver_student_rows)
            summary_database_gold = populate_gold_all(connection, gold_tables_by_name)
        finally:
            connection.close()

    # ------ Resumen final ------
    summary: Dict[str, Dict[str, Any]] = {
        "filter_out_algebra"    : summary_filter,
        "group_by_test"         : summary_group_test,
        "group_by_student"      : summary_group_student,
        "database"              : summary_database_base,
        "gold"                  : summary_database_gold,
    }
    return dataframe_silver_student_rows, summary
