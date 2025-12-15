from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd


def calculate_kpi_1_2_1(
    db      : Session,
    cohorte : int = 2022
) -> Dict[str, Any]:
    """
    KPI 1.2.1 - Correlación PAES/PDT vs Nota 1er bimestre

    Args:
        db      : Sesión de base de datos SQLAlchemy
        cohorte : Año de ingreso de la cohorte (por defecto 2022)

    Returns:
        Dict con «value» (float), «meta» (dict con n, detalles, etc.)
    """

    # ------ Consulta Gold (puntaje_ingreso + nota_b1) ------
    query = text("""
        SELECT
            g.id_estudiante,
            g.tipo_prueba,
            g.puntaje_ingreso,
            g.nota_b1
        FROM gold_kpi_b1_student g
        WHERE g.cohorte = :cohorte
          AND g.puntaje_ingreso IS NOT NULL
          AND g.nota_b1 IS NOT NULL
        ORDER BY g.id_estudiante
    """)

    # ------ Ejecutar query y convertir a DataFrame ------
    result  = db.execute(query, {"cohorte": cohorte})
    df      = pd.DataFrame(
        result.fetchall(),
        columns=["id_estudiante", "tipo_prueba", "puntaje_ingreso", "nota_b1"],
    )

    # ------ Validación: mínimo de observaciones para correlación ------
    if len(df) < 2:
        return {
            "value": None,
            "meta": {
                "cohorte"   : cohorte,
                "n"         : len(df),
                "error"     : "Insuficientes datos para calcular correlación (se requieren al menos 2 observaciones)",
            },
        }

    # ------ Cálculo: correlación puntaje_ingreso vs nota_b1 ------
    r = df["puntaje_ingreso"].corr(df["nota_b1"])

    # ------ Validación: correlación inválida (posible varianza cero) ------
    if pd.isna(r):
        return {
            "value" : None,
            "meta"  : {
                "cohorte"   : cohorte,
                "n"         : len(df),
                "error"     : "No se pudo calcular la correlación (posible varianza cero)",
            },
        }

    # ------ Salida: value + estadísticas descriptivas ------
    result_kpi = {
        "value" : float(r),
        "meta"  : {
            "cohorte"           : cohorte,
            "n"                 : len(df),
            "puntaje_ingreso"   : {
                "min"               : float(df["puntaje_ingreso"].min()),
                "max"               : float(df["puntaje_ingreso"].max()),
                "promedio"          : float(df["puntaje_ingreso"].mean()),
                "std"               : float(df["puntaje_ingreso"].std()),
            },
            "nota_b1": {
                "min"       : float(df["nota_b1"].min()),
                "max"       : float(df["nota_b1"].max()),
                "promedio"  : float(df["nota_b1"].mean()),
                "std"       : float(df["nota_b1"].std()),
            },
            "distribucion_tipo_prueba": df["tipo_prueba"].value_counts().to_dict(),
        },
    }
    return result_kpi
