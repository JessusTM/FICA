from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd


def calculate_kpi_1_2_2(
    db      : Session,
    cohorte : int = 2022
) -> Dict[str, Any]:
    """
    KPI 1.2.2 - Correlación Diagnóstico Matemáticas vs Nota 1er bimestre

    Args:
        db      : Sesión de base de datos SQLAlchemy
        cohorte : Año de ingreso de la cohorte (por defecto 2022)

    Returns:
        Dict con «value» (float), «meta» (dict con n, detalles, etc.)
    """
    query = text("""
        SELECT
            g.id_estudiante,
            g.diagnostico,
            g.nota_b1
        FROM gold_kpi_b1_student g
        WHERE g.cohorte = :cohorte
          AND g.diagnostico IS NOT NULL
          AND g.nota_b1 IS NOT NULL
        ORDER BY g.id_estudiante
    """)

    result  = db.execute(query, {"cohorte": cohorte})
    df      = pd.DataFrame(result.fetchall(), columns=[
        'id_estudiante', 'diagnostico', 'nota_b1'
    ])

    if len(df) < 2:
        return {
            "value" : None,
            "meta"  : {
                "cohorte"   : cohorte,
                "n"         : len(df),
                "error"     : "Insuficientes datos para calcular correlación (se requieren al menos 2 observaciones)"
            }
        }

    r = df['diagnostico'].corr(df['nota_b1'])

    if pd.isna(r):
        return {
            "value" : None,
            "meta"  : {
                "cohorte"   : cohorte,
                "n"         : len(df),
                "error"     : "No se pudo calcular la correlación (posible varianza cero)"
            }
        }

    result_kpi = {
        "value" : float(r),
        "meta"  : {
            "cohorte"       : cohorte,
            "n"             : len(df),
            "diagnostico"   : {
                "min"       : float(df['diagnostico'].min()),
                "max"       : float(df['diagnostico'].max()),
                "promedio"  : float(df['diagnostico'].mean()),
                "std"       : float(df['diagnostico'].std())
            },
            "nota_b1": {
                "min"       : float(df['nota_b1'].min()),
                "max"       : float(df['nota_b1'].max()),
                "promedio"  : float(df['nota_b1'].mean()),
                "std"       : float(df['nota_b1'].std())
            }
        }
    }
    return result_kpi 
