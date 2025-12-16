from __future__ import annotations

from typing import Dict, Any
import pandas as pd


# Helpers comunes
def _replace_nan_with_none(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Reemplaza NaN/NaT/Inf/-Inf por None en un DataFrame.

    Contexto:
    - Antes de insertar en PostgreSQL con psycopg2.

    Para qué:
    - Pandas usa NaN/Inf, pero psycopg2 espera None para NULL.
    - Los valores Inf/-Inf no son JSON compliant y causan errores.

    Dónde:
    - Usado por _dataframe_to_records() en este mismo archivo.
    """
    import numpy as np
    dataframe_clean = dataframe.copy()

    # Replace NaN and NaT with None
    dataframe_clean = dataframe_clean.where(pd.notna(dataframe_clean), None)

    # Replace inf and -inf with None for numeric columns
    numeric_cols = dataframe_clean.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        dataframe_clean[col] = dataframe_clean[col].replace([np.inf, -np.inf], None)

    return dataframe_clean


def _dataframe_to_records(dataframe: pd.DataFrame, ordered_columns: list[str]) -> list[tuple]:
    """
    Convierte un DataFrame a lista de tuplas (records) en el orden exacto de columnas.

    Contexto:
    - Preparación para cursor.executemany().

    Para qué:
    - Garantizar que el orden de valores coincida con el INSERT.

    Dónde:
    - Usado por insert_* en este archivo.
    """
    dataframe_ordered   = dataframe[ordered_columns].copy()
    dataframe_clean     = _replace_nan_with_none(dataframe_ordered)
    records             = list(dataframe_clean.itertuples(index=False, name=None))
    return records


def _executemany_in_batches(
    cursor,
    query       : str,
    records     : list[tuple],
    batch_size  : int = 1000,
) -> int:
    """
    Ejecuta un INSERT (o UPSERT) con cursor.executemany() en lotes.

    Contexto:
    - psycopg2 puede volverse lento si haces 1 commit por fila o si mandas demasiadas filas
      sin control. Este helper lo deja simple y razonable.

    Para qué:
    - Insertar N filas en grupos de tamaño fijo y devolver cuántas filas se intentaron insertar.

    Dónde:
    - Usado por insert_gold_* en este archivo.
    """
    if len(records) == 0:
        inserted_count = 0
        return inserted_count

    inserted_count  = 0
    start_index     = 0

    while start_index < len(records):
        end_index       = start_index + batch_size
        records_batch   = records[start_index:end_index]

        cursor.executemany(query, records_batch)

        inserted_count += len(records_batch)
        start_index     = end_index
    return inserted_count


# Inserts Gold
def insert_gold_kpi_b1_student(conn, dataframe_gold_kpi_b1_student: pd.DataFrame) -> int:
    """
    Inserta/actualiza la tabla Gold: gold_kpi_b1_student.

    Contexto:
    - Capa Gold en DB (PostgreSQL).
    - DataFrame viene desde build_gold.build_gold_kpi_b1_student.

    Para qué:
    - Evitar joins grandes en KPIs 1.2.1, 1.2.2, 1.3, 1.7, 1.8.
      Esta tabla ya trae: puntaje_ingreso, diagnostico y nota_b1 por estudiante/cohorte.

    Dónde se usa:
    - Llamado por populate_gold_all().
    """
    columnas_insert = [
        "cohorte",
        "id_estudiante",
        "tipo_prueba",
        "puntaje_ingreso",
        "diagnostico",
        "nota_b1",
    ]
    records = _dataframe_to_records(dataframe_gold_kpi_b1_student, columnas_insert)
    query   = """
        INSERT INTO gold_kpi_b1_student (
            cohorte,
            id_estudiante,
            tipo_prueba,
            puntaje_ingreso,
            diagnostico,
            nota_b1
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (cohorte, id_estudiante)
        DO UPDATE SET
            tipo_prueba      = EXCLUDED.tipo_prueba,
            puntaje_ingreso  = EXCLUDED.puntaje_ingreso,
            diagnostico      = EXCLUDED.diagnostico,
            nota_b1          = EXCLUDED.nota_b1
    """

    cursor = conn.cursor()
    try:
        inserted_or_updated_count = _executemany_in_batches(
            cursor      = cursor,
            query       = query,
            records     = records,
            batch_size  = 1000,
        )
        conn.commit()
        return inserted_or_updated_count
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()


def insert_gold_kpi_student_ramos(conn, dataframe_gold_kpi_student_ramos: pd.DataFrame) -> int:
    """
    Inserta/actualiza la tabla Gold: gold_kpi_student_ramos.

    Contexto:
    - DataFrame viene desde build_gold.build_gold_kpi_student_ramos.

    Para qué:
    - KPI 1.1 y KPI 1.5 dependen de total_ramos.
      Con esto evitas contar ramos desde rendimiento_ramo cada vez.

    Dónde se usa:
    - Llamado por populate_gold_all().
    """
    columnas_insert = ["cohorte", "id_estudiante", "total_ramos"]
    records         = _dataframe_to_records(dataframe_gold_kpi_student_ramos, columnas_insert)
    query           = """
        INSERT INTO gold_kpi_student_ramos (
            cohorte,
            id_estudiante,
            total_ramos
        )
        VALUES (%s, %s, %s)
        ON CONFLICT (cohorte, id_estudiante)
        DO UPDATE SET
            total_ramos = EXCLUDED.total_ramos
    """

    cursor = conn.cursor()
    try:
        inserted_or_updated_count = _executemany_in_batches(
            cursor      = cursor,
            query       = query,
            records     = records,
            batch_size  = 1000,
        )
        conn.commit()
        return inserted_or_updated_count
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()


def insert_gold_kpi_student_aprueba8(conn, dataframe_gold_kpi_student_aprueba8: pd.DataFrame) -> int:
    """
    Inserta/actualiza la tabla Gold: gold_kpi_student_aprueba8.

    Contexto:
    - DataFrame viene desde build_gold.build_gold_kpi_student_aprueba8.

    Para qué:
    - KPI 1.4 usa aprueba_8 por estudiante/cohorte.
      Con esto evitas recalcular “8 bimestres + nota mínima >= 4.0” dentro del KPI.

    Dónde se usa:
    - Llamado por populate_gold_all().
    """
    columnas_insert = ["cohorte", "id_estudiante", "aprueba_8"]
    records         = _dataframe_to_records(dataframe_gold_kpi_student_aprueba8, columnas_insert)
    query           = """
        INSERT INTO gold_kpi_student_aprueba8 (
            cohorte,
            id_estudiante,
            aprueba_8
        )
        VALUES (%s, %s, %s)
        ON CONFLICT (cohorte, id_estudiante)
        DO UPDATE SET
            aprueba_8 = EXCLUDED.aprueba_8
    """

    cursor = conn.cursor()
    try:
        inserted_or_updated_count = _executemany_in_batches(
            cursor      = cursor,
            query       = query,
            records     = records,
            batch_size  = 1000,
        )
        conn.commit()
        return inserted_or_updated_count
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()


def populate_gold_all(conn, gold_tables: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Inserta/actualiza todas las tablas Gold.

    Contexto:
    - Recibe el dict que produce build_gold.build_all_gold().

    Para qué:
    - Dejar la capa Gold lista para que los KPIs consulten con joins mínimos.

    Dónde:
    - Se llama desde el pipeline ETL cuando decidas activar Gold.
    """
    dataframe_gold_kpi_b1_student       = gold_tables.get("gold_kpi_b1_student", pd.DataFrame())
    dataframe_gold_kpi_student_ramos    = gold_tables.get("gold_kpi_student_ramos", pd.DataFrame())
    dataframe_gold_kpi_student_aprueba8 = gold_tables.get("gold_kpi_student_aprueba8", pd.DataFrame())

    inserted_b1_student         = insert_gold_kpi_b1_student(conn, dataframe_gold_kpi_b1_student)
    inserted_student_ramos      = insert_gold_kpi_student_ramos(conn, dataframe_gold_kpi_student_ramos)
    inserted_student_aprueba8   = insert_gold_kpi_student_aprueba8(conn, dataframe_gold_kpi_student_aprueba8)

    summary = {
        "gold_kpi_b1_student"       : inserted_b1_student,
        "gold_kpi_student_ramos"    : inserted_student_ramos,
        "gold_kpi_student_aprueba8" : inserted_student_aprueba8,
    }
    return summary
