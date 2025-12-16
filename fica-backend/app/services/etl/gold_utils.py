from __future__ import annotations

from typing import Dict, Set
import pandas as pd


def convert_to_int_or_none(value):
    """
    Convierte un valor a int de forma tolerante.

    Contexto:
    - Se usa en el ETL (paso Silver → Gold) para normalizar columnas que vienen como texto
      o float (por ejemplo, "1", 1.0, "2022").

    Para qué:
    - Evitar errores al comparar / agrupar (groupby) por columnas como cohorte, semestre, bimestre, id_alumno.

    Dónde:
    - Consumido por app/services/etl/build_gold.py (builders Gold)
    """
    if pd.isna(value):
        return None
    try:
        return int(float(value))
    except Exception:
        return None


def convert_to_float_or_none(value):
    """
    Convierte un valor a float de forma tolerante.

    Contexto:
    - Se usa en el ETL (paso Silver → Gold) para normalizar notas y puntajes.

    Para qué:
    - Evitar errores al calcular promedios, mínimos o correlaciones posteriores.

    Dónde:
    - Consumido por app/services/etl/build_gold.py (builders Gold)
    """
    if pd.isna(value):
        return None
    try:
        return float(value)
    except Exception:
        return None


# Helpers: columnas base estudiante
def add_student_identity_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega y normaliza columnas base de identidad del estudiante.

    Qué hace:
    - Crea:
      - cohorte (desde año_ingreso)
      - id_estudiante (desde id_alumno)
      - tipo_prueba (PAES/PDT desde tipo_ingreso)
      - diagnostico (desde diagnostico_matematica)

    Para qué:
    - Dejar un esqueleto por estudiante/cohorte que se reutiliza en varias tablas Gold.

    Dónde:
    - Se usa por build_gold_kpi_b1_student (tabla gold_kpi_b1_student)
    - De forma indirecta soporta KPIs 1.2.x, 1.3, 1.6, 1.7, 1.8 porque todos parten
      de cohorte + estudiante + predictores.

    Contexto:
    - ETL Silver → Gold (no toca DB aquí, solo prepara DataFrames).
    """
    dataframe_copy = dataframe.copy()

    dataframe_copy["cohorte"]       = dataframe_copy["año_ingreso"].map(convert_to_int_or_none)
    dataframe_copy["id_estudiante"] = dataframe_copy["id_alumno"].map(convert_to_int_or_none)

    dataframe_copy["tipo_prueba"]   = None
    series_tipo_prueba              = dataframe_copy["tipo_ingreso"].astype(str).str.upper()
    dataframe_copy.loc[dataframe_copy["tipo_ingreso"].notna(), "tipo_prueba"] = series_tipo_prueba
    dataframe_copy["diagnostico"]   = dataframe_copy["diagnostico_matematica"].map(convert_to_float_or_none)
    return dataframe_copy


def add_puntaje_ingreso_column(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega la columna puntaje_ingreso según el tipo de prueba (PAES o PDT).

    Qué hace:
    - Si tipo_prueba == "PAES"  : usa paes_promedio_m1_comprension_lectora
    - Si tipo_prueba == "PDT"   :  usa pdt_promedio_matematicas_lenguaje

    Para qué:
    - Unificar en una sola variable el predictor de ingreso definido en el PDF
      para KPIs de correlación y perfiles.

    Dónde:
    - Se usa principalmente en build_gold_kpi_b1_student (gold_kpi_b1_student)
    - Luego, KPIs 1.2.1 / 1.3 / 1.6 / 1.7 / 1.8 consumen esta columna desde Gold.
    """
    dataframe_copy = dataframe.copy()
    dataframe_copy["puntaje_ingreso"] = None

    series_puntaje_paes = dataframe_copy["paes_promedio_m1_comprension_lectora"].map(convert_to_float_or_none)
    series_puntaje_pdt  = dataframe_copy["pdt_promedio_matematicas_lenguaje"].map(convert_to_float_or_none)

    filtro_es_paes  = dataframe_copy["tipo_prueba"] == "PAES"
    filtro_es_pdt   = dataframe_copy["tipo_prueba"] == "PDT"

    dataframe_copy.loc[filtro_es_paes, "puntaje_ingreso"]   = series_puntaje_paes[filtro_es_paes]
    dataframe_copy.loc[filtro_es_pdt, "puntaje_ingreso"]    = series_puntaje_pdt[filtro_es_pdt]
    return dataframe_copy


def add_period_and_grade_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega columnas normalizadas de período académico y nota final.

    Qué hace:
    - Crea:
      - semestre_normalizado
      - bimestre_normalizado
      - nota_final_normalizada

    Para qué:
    - Facilitar filtros como primer bimestre y cálculos como promedio/mínimo de notas.

    Dónde:
    - Se usa en compute_promedio_nota_b1 (gold_kpi_b1_student)
    """
    dataframe_copy = dataframe.copy()

    dataframe_copy["semestre_normalizado"]      = dataframe_copy["semestre"].map(convert_to_int_or_none)
    dataframe_copy["bimestre_normalizado"]      = dataframe_copy["bimestre"].map(convert_to_int_or_none)
    dataframe_copy["nota_final_normalizada"]    = dataframe_copy["nota_final"].map(convert_to_float_or_none)
    return dataframe_copy


def compute_promedio_nota_b1(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la nota promedio del primer bimestre (B1) por estudiante y cohorte.

    Qué hace:
    - Filtra filas con (semestre_normalizado == 1) y (bimestre_normalizado == 1)
    - Agrupa por (cohorte, id_estudiante)
    - Promedia nota_final_normalizada
    - Devuelve DataFrame con: cohorte, id_estudiante, nota_b1

    Para qué:
    - Materializar en Gold la variable «Nota 1er bimestre» usada en:
      KPI 1.2.1, KPI 1.2.2, KPI 1.3, KPI 1.7, KPI 1.8.

    Dónde:
    - Consumido por build_gold_kpi_b1_student (tabla gold_kpi_b1_student)
    """
    dataframe_copy = dataframe.copy()

    dataframe_primer_bimestre = dataframe_copy[
        (dataframe_copy["semestre_normalizado"] == 1) &
        (dataframe_copy["bimestre_normalizado"] == 1)
    ].copy()

    dataframe_primer_bimestre = dataframe_primer_bimestre.dropna(
        subset=["cohorte", "id_estudiante", "nota_final_normalizada"]
    )

    dataframe_promedio_nota_b1 = (
        dataframe_primer_bimestre
        .groupby(["cohorte", "id_estudiante"], as_index=False)["nota_final_normalizada"]
        .mean()
        .rename(columns={"nota_final_normalizada": "nota_b1"})
    )
    return dataframe_promedio_nota_b1


def build_base_student_table(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Construye una tabla base por estudiante y cohorte con variables de ingreso.

    Qué hace:
    - Selecciona: cohorte, id_estudiante, tipo_prueba, puntaje_ingreso, diagnostico
    - Elimina nulos en cohorte/id_estudiante
    - Deja 1 fila por (cohorte, id_estudiante)

    Para qué:
    - Usar esta base y luego hacer merge con nota_b1 para crear gold_kpi_b1_student.

    Dónde:
    - Consumido por build_gold_kpi_b1_student (tabla gold_kpi_b1_student)
    """
    columnas_base = ["cohorte", "id_estudiante", "tipo_prueba", "puntaje_ingreso", "diagnostico"]

    dataframe_base = dataframe[columnas_base].copy()
    dataframe_base = dataframe_base.dropna(subset=["cohorte", "id_estudiante"])
    dataframe_base = dataframe_base.drop_duplicates(subset=["cohorte", "id_estudiante"])
    return dataframe_base


# Helpers: ramos por estudiante
def add_ramos_normalized_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega columnas normalizadas necesarias para contar ramos por estudiante.

    Qué hace:
    - Crea:
      - cohorte, id_estudiante
      - anio_academico_normalizado, semestre_academico_normalizado, bimestre_academico_normalizado

    Para qué:
    - Asegurar que el conteo de ramos funcione aunque los datos vengan como texto o float.

    Dónde:
    - Consumido por build_gold_kpi_student_ramos (tabla gold_kpi_student_ramos)
    - Esa tabla soporta KPI 1.1 y KPI 1.5 (desviación vs 8 y deserción/no completan 8).
    """
    dataframe_copy = dataframe.copy()

    dataframe_copy["cohorte"]       = dataframe_copy["año_ingreso"].map(convert_to_int_or_none)
    dataframe_copy["id_estudiante"] = dataframe_copy["id_alumno"].map(convert_to_int_or_none)

    dataframe_copy["anio_academico_normalizado"]        = dataframe_copy["año"].map(convert_to_int_or_none)
    dataframe_copy["semestre_academico_normalizado"]    = dataframe_copy["semestre"].map(convert_to_int_or_none)
    dataframe_copy["bimestre_academico_normalizado"]    = dataframe_copy["bimestre"].map(convert_to_int_or_none)
    return dataframe_copy


def filter_valid_rows_for_ramos(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra filas mínimamente válidas para el conteo de ramos.

    Qué hace:
    - Exige columnas clave no nulas:
      cohorte, id_estudiante, año/semestre/bimestre normalizados, código y nombre de asignatura.

    Para qué:
    - Evitar contar «ramos fantasma» por filas incompletas.

    Dónde:
    - Consumido por build_gold_kpi_student_ramos (tabla gold_kpi_student_ramos)
    """
    columnas_requeridas = [
        "cohorte",
        "id_estudiante",
        "anio_academico_normalizado",
        "semestre_academico_normalizado",
        "bimestre_academico_normalizado",
        "codigo_asignatura",
        "nombre_asignatura",
    ]

    dataframe_valid = dataframe.dropna(subset=columnas_requeridas).copy()
    return dataframe_valid


def count_unique_ramos_by_student(dataframe_valid: pd.DataFrame) -> pd.DataFrame:
    """
    Cuenta ramos únicos por (cohorte, id_estudiante).

    Qué hace:
    - Define «ramo único» como combinación:
      (año, semestre, bimestre, codigo_asignatura, modulo, nombre_asignatura)
    - Elimina duplicados en esa clave
    - Cuenta filas únicas por estudiante

    Para qué:
    - Materializar «total_ramos» en Gold para KPIs:
      - KPI 1.1 (desviación promedio respecto a 8)
      - KPI 1.5 (tasa de no completar 8)

    Dónde:
    - Consumido por build_gold_kpi_student_ramos (tabla gold_kpi_student_ramos)
    """
    columnas_ramo_unico = [
        "anio_academico_normalizado",
        "semestre_academico_normalizado",
        "bimestre_academico_normalizado",
        "codigo_asignatura",
        "modulo",
        "nombre_asignatura",
    ]

    columnas_para_duplicados    = ["cohorte", "id_estudiante"] + columnas_ramo_unico
    dataframe_ramos_unicos      = dataframe_valid.drop_duplicates(subset=columnas_para_duplicados)

    dataframe_conteo_ramos = (
        dataframe_ramos_unicos
        .groupby(["cohorte", "id_estudiante"])
        .size()
        .reset_index(name="total_ramos")
    )

    dataframe_conteo_ramos["total_ramos"] = dataframe_conteo_ramos["total_ramos"].astype(int)
    return dataframe_conteo_ramos


# Helpers: aprueba 8 bimestres
def normalize_columns_for_aprueba8(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza columnas mínimas para calcular 'aprueba_8'.

    Qué hace:
    - Crea:
      cohorte, id_estudiante, semestre_normalizado, bimestre_normalizado, nota_final_normalizada
    - Filtra filas sin esos datos.

    Para qué:
    - Tener un dataset consistente de «notas por bimestre» para decidir aprobación.

    Dónde:
    - Consumido por build_gold_kpi_student_aprueba8 (tabla gold_kpi_student_aprueba8)
    """
    dataframe_copy = dataframe.copy()

    dataframe_copy["cohorte"]       = dataframe_copy["año_ingreso"].map(convert_to_int_or_none)
    dataframe_copy["id_estudiante"] = dataframe_copy["id_alumno"].map(convert_to_int_or_none)

    dataframe_copy["semestre_normalizado"]      = dataframe_copy["semestre"].map(convert_to_int_or_none)
    dataframe_copy["bimestre_normalizado"]      = dataframe_copy["bimestre"].map(convert_to_int_or_none)
    dataframe_copy["nota_final_normalizada"]    = dataframe_copy["nota_final"].map(convert_to_float_or_none)

    dataframe_copy = dataframe_copy.dropna(
        subset=[
            "cohorte",
            "id_estudiante",
            "semestre_normalizado",
            "bimestre_normalizado",
            "nota_final_normalizada",
        ]
    )
    return dataframe_copy


def add_bimestre_key_column(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega una clave simple por bimestre: clave_bimestre = semestre*10 + bimestre.

    Para qué:
    - Identificar bimestres de forma simple (ej: 1-1 => 11, 2-1 => 21).
    - Facilitar comparaciones de “tiene todos los bimestres”.

    Dónde:
    - Consumido por build_gold_kpi_student_aprueba8 (tabla gold_kpi_student_aprueba8)
    """
    dataframe_copy = dataframe.copy()

    dataframe_copy["clave_bimestre"] = (
        (dataframe_copy["semestre_normalizado"] * 10) +
        dataframe_copy["bimestre_normalizado"]
    )
    return dataframe_copy


def compute_first_8_bimestres_targets(dataframe: pd.DataFrame) -> Dict[int, Set[int]]:
    """
    Define cuáles son los 8 primeros bimestres de cada cohorte.

    Qué hace:
    - Para cada cohorte:
      - toma bimestres únicos (semestre,bimestre)
      - ordena
      - selecciona los primeros 8
      - los guarda como conjunto (set) de claves_bimestre

    Para qué:
    - Tener la «lista objetivo» de bimestres que un estudiante debe tener para considerarse
      que completó el ciclo (para KPI 1.4).

    Dónde:
    - Consumido por build_gold_kpi_student_aprueba8 (tabla gold_kpi_student_aprueba8)
    """
    targets_por_cohorte: Dict[int, Set[int]] = {}

    for cohorte, dataframe_cohorte in dataframe.groupby("cohorte"):
        dataframe_bimestres = dataframe_cohorte[
            ["semestre_normalizado", "bimestre_normalizado", "clave_bimestre"]
        ].drop_duplicates()

        dataframe_bimestres_ordenados = dataframe_bimestres.sort_values(
            ["semestre_normalizado", "bimestre_normalizado"]
        )

        lista_8_bimestres = dataframe_bimestres_ordenados["clave_bimestre"].head(8).tolist()
        targets_por_cohorte[int(cohorte)] = set(lista_8_bimestres)

    return targets_por_cohorte


def evaluate_aprueba8_by_student(
    dataframe: pd.DataFrame,
    targets_por_cohorte: Dict[int, Set[int]],
) -> pd.DataFrame:
    """
    Calcula el indicador aprueba_8 por estudiante.

    Qué hace:
    - Para cada (cohorte, estudiante):
      1) Verifica que existan 8 bimestres objetivo para esa cohorte
      2) Verifica que el estudiante tenga registros en esos 8 bimestres
      3) Calcula la nota mínima en esos bimestres y exige >= 4.0
      4) Retorna aprueba_8 = 1 o 0

    Para qué:
    - Materializar en Gold un indicador base para KPI 1.4
      (“aprueban los 8 bimestres sin reprobar ramos”).

    Dónde:
    - Consumido por build_gold_kpi_student_aprueba8 (tabla gold_kpi_student_aprueba8)
    """
    filas_resultado = []

    for (cohorte, id_estudiante), dataframe_estudiante in dataframe.groupby(["cohorte", "id_estudiante"]):
        cohorte_int     = int(cohorte)
        estudiante_int  = int(id_estudiante)

        targets_bimestres = targets_por_cohorte.get(cohorte_int, set())
        if len(targets_bimestres) < 8:
            # No hay definición completa de 8 bimestres para esta cohorte: se marca como False.
            filas_resultado.append((cohorte_int, estudiante_int, False))
            continue

        bimestres_presentes     = set(dataframe_estudiante["clave_bimestre"].drop_duplicates().tolist())
        estudiante_tiene_todos  = targets_bimestres.issubset(bimestres_presentes)

        if not estudiante_tiene_todos:
            # El estudiante no tiene registros en todos los bimestres objetivo: se marca como False.
            filas_resultado.append((cohorte_int, estudiante_int, False))
            continue

        dataframe_target = dataframe_estudiante[
            dataframe_estudiante["clave_bimestre"].isin(list(targets_bimestres))
        ].copy()

        nota_minima         = dataframe_target["nota_final_normalizada"].min()
        indicador_aprueba_8 = False
        if nota_minima is not None and nota_minima >= 4.0:
            indicador_aprueba_8 = True

        filas_resultado.append((cohorte_int, estudiante_int, indicador_aprueba_8))

    dataframe_resultado = pd.DataFrame(
        filas_resultado,
        columns=["cohorte", "id_estudiante", "aprueba_8"],
    )

    # La columna ya viene como booleano Python (True/False), compatible con PostgreSQL boolean.
    return dataframe_resultado
