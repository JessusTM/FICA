from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd


def calculate_kpi_1_1(
    db      : Session,
    cohorte : int = 2022
) -> Dict[str, Any]:
    """
    KPI 1.1 - Desviación promedio de ramos cursados respecto al ideal (8)

    Args:
        db      : Sesión de base de datos SQLAlchemy
        cohorte : Año de ingreso de la cohorte (por defecto 2022)

    Returns:
        Dict con «value» (float), «meta» (dict con E, desviaciones, etc.)
    """

    # ------ Consulta base (cohorte + total_ramos desde Gold) ------
    query = text("""
        SELECT
            e.id_estudiante,
            COALESCE(g.total_ramos, 0) as total_ramos
        FROM estudiantes e
        LEFT JOIN gold_kpi_student_ramos g
            ON g.id_estudiante = e.id_estudiante
            AND g.cohorte = e.anio_ingreso
        WHERE e.anio_ingreso = :cohorte
        ORDER BY e.id_estudiante
    """)

    # ------ Ejecutar query y convertir a DataFrame ------
    result  = db.execute(query, {"cohorte": cohorte})
    df      = pd.DataFrame(result.fetchall(), columns=["id_estudiante", "total_ramos"])

    # ------ Validación: cohorte sin datos ------
    if len(df) == 0:
        return {
            "value" : None,
            "meta"  : {
                "cohorte"   : cohorte,
                "E"         : 0,
                "error"     : "No se encontraron estudiantes para la cohorte especificada",
            },
        }

    # ------ Cálculo: desviación por estudiante vs ideal(8) ------
    df["De"] = df["total_ramos"] - 8

    # ------ Agregación: tamaño de cohorte y promedio de desviación ------
    E = len(df)
    D = df["De"].mean()

    # ------ Salida: value + métricas resumen ------
    result_value = {
        "value": float(D),
        "meta": {
            "cohorte"                       : cohorte,
            "E"                             : E,
            "desviacion_promedio"           : float(D),
            "desviaciones_por_estudiante"   : {
                "min": float(df["De"].min()),
                "max": float(df["De"].max()),
                "std": float(df["De"].std()),
            },
            "distribucion_ramos": {
                "min"       : int(df["total_ramos"].min()),
                "max"       : int(df["total_ramos"].max()),
                "promedio"  : float(df["total_ramos"].mean()),
                "mediana"   : float(df["total_ramos"].median()),
            },
        },
    }
    return result_value
