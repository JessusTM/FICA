from __future__ import annotations

from typing import Dict
import pandas as pd

from app.services.etl.gold_utils import (
    add_student_identity_columns,
    add_puntaje_ingreso_column,
    add_period_and_grade_columns,
    compute_promedio_nota_b1,
    build_base_student_table,
    add_ramos_normalized_columns,
    filter_valid_rows_for_ramos,
    count_unique_ramos_by_student,
    normalize_columns_for_aprueba8,
    add_bimestre_key_column,
    compute_first_4_bimestres_targets,
    evaluate_aprueba8_by_student,
)


def build_gold_kpi_b1_student(dataframe_silver_student_rows: pd.DataFrame) -> pd.DataFrame:
    """
    Construye la tabla Gold: gold_kpi_b1_student.

    Contexto:
    - ETL Silver → Gold (sobre el DataFrame df3 que sale del pipeline).
    - Esta tabla reduce joins posteriores: deja 1 fila por estudiante con variables de ingreso
      y la nota promedio del primer bimestre.

    Para qué:
    - Soporta KPIs: 1.2.1, 1.2.2, 1.3, 1.7, 1.8 (todos usan nota_b1 + predictores).

    Dónde se usa:
    - Se invoca desde el pipeline ETL cuando se quiera generar/insertar la capa Gold.
    """
    # ------ Normalización base ------
    dataframe_con_identidad         = add_student_identity_columns(dataframe_silver_student_rows)
    dataframe_con_puntaje           = add_puntaje_ingreso_column(dataframe_con_identidad)
    dataframe_con_periodo_y_nota    = add_period_and_grade_columns(dataframe_con_puntaje)

    # ------ Nota 1er bimestre ------
    dataframe_promedio_nota_b1      = compute_promedio_nota_b1(dataframe_con_periodo_y_nota)

    # ------ Base por estudiante + merge ------
    dataframe_base_estudiantes      = build_base_student_table(dataframe_con_periodo_y_nota)

    dataframe_gold_kpi_b1_student   = dataframe_base_estudiantes.merge(
        dataframe_promedio_nota_b1,
        on  = ["cohorte", "id_estudiante"],
        how = "left",
    )

    columnas_salida = [
        "cohorte",
        "id_estudiante",
        "tipo_prueba",
        "puntaje_ingreso",
        "diagnostico",
        "nota_b1",
    ]
    dataframe_gold_kpi_b1_student = dataframe_gold_kpi_b1_student[columnas_salida].copy()
    dataframe_gold_kpi_b1_student = dataframe_gold_kpi_b1_student.sort_values(
        ["cohorte", "id_estudiante"]
    ).reset_index(drop=True)
    return dataframe_gold_kpi_b1_student


def build_gold_kpi_student_ramos(dataframe_silver_student_rows: pd.DataFrame) -> pd.DataFrame:
    """
    Construye la tabla Gold: gold_kpi_student_ramos.

    Contexto:
    - ETL Silver → Gold.
    - Se crea una tabla compacta con 1 fila por estudiante/cohorte y su conteo de ramos.

    Para qué:
    - Soporta KPIs: 1.1 y 1.5 (desviación vs 8 y tasa de deserción/no completan 8).

    Dónde se usa:
    - Se invoca desde el pipeline ETL cuando se quiera generar/insertar la capa Gold.
    """
    # ------ Normalización ------
    dataframe_con_columnas_ramos = add_ramos_normalized_columns(dataframe_silver_student_rows)

    # ------ Filtrado ------
    dataframe_valido = filter_valid_rows_for_ramos(dataframe_con_columnas_ramos)

    # ------ Conteo ------
    dataframe_conteo_ramos              = count_unique_ramos_by_student(dataframe_valido)
    dataframe_gold_kpi_student_ramos    = dataframe_conteo_ramos[
        ["cohorte", "id_estudiante", "total_ramos"]
    ].copy()

    dataframe_gold_kpi_student_ramos    = dataframe_gold_kpi_student_ramos.sort_values(
        ["cohorte", "id_estudiante"]
    ).reset_index(drop=True)
    return dataframe_gold_kpi_student_ramos


def build_gold_kpi_student_aprueba8(dataframe_silver_student_rows: pd.DataFrame) -> pd.DataFrame:
    """
    Construye la tabla Gold: gold_kpi_student_aprueba8.

    Contexto:
    - ETL Silver → Gold.
    - Se materializa un indicador binario por estudiante que resume si completó y aprobó
      los 4 primeros bimestres definidos para su cohorte.

    Para qué:
    - Soporta KPI 1.4 (estudiantes que aprueban los 4 bimestres sin reprobar ramos).

    Dónde se usa:
    - Se invoca desde el pipeline ETL cuando se quiera generar/insertar la capa Gold.
    """
    # ------ Normalización ------
    dataframe_columnas_aprueba8     = normalize_columns_for_aprueba8(dataframe_silver_student_rows)
    dataframe_con_clave_bimestre    = add_bimestre_key_column(dataframe_columnas_aprueba8)

    # ------ Targets 4 bimestres ------
    targets_por_cohorte = compute_first_4_bimestres_targets(dataframe_con_clave_bimestre)

    # ------ Evaluación ------
    dataframe_resultado_aprueba8    = evaluate_aprueba8_by_student(
        dataframe_con_clave_bimestre,
        targets_por_cohorte,
    )

    dataframe_gold_kpi_student_aprueba8 = dataframe_resultado_aprueba8[
        ["cohorte", "id_estudiante", "aprueba_8"]
    ].copy()

    dataframe_gold_kpi_student_aprueba8 = dataframe_gold_kpi_student_aprueba8.sort_values(
        ["cohorte", "id_estudiante"]
    ).reset_index(drop=True)
    return dataframe_gold_kpi_student_aprueba8


def build_all_gold(dataframe_silver_student_rows: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Construye todas las tablas Gold requeridas para simplificar los KPIs.

    Contexto:
    - ETL Silver → Gold.
    - Este método es el “orquestador” de la construcción de tablas Gold en memoria.

    Para qué:
    - Entregar un diccionario {nombre_tabla: dataframe} listo para insertar en DB
      (en el siguiente paso: populate_gold.py).

    Dónde se usa:
    - Se invoca desde el pipeline ETL cuando se quiera recalcular toda la capa Gold.
    """
    # ------ Construcción de tablas Gold ------
    dataframe_gold_kpi_b1_student       = build_gold_kpi_b1_student(dataframe_silver_student_rows)
    dataframe_gold_kpi_student_ramos    = build_gold_kpi_student_ramos(dataframe_silver_student_rows)
    dataframe_gold_kpi_student_aprueba8 = build_gold_kpi_student_aprueba8(dataframe_silver_student_rows)

    result = {
        "gold_kpi_b1_student"       : dataframe_gold_kpi_b1_student,
        "gold_kpi_student_ramos"    : dataframe_gold_kpi_student_ramos,
        "gold_kpi_student_aprueba8" : dataframe_gold_kpi_student_aprueba8,
    }
    return result
