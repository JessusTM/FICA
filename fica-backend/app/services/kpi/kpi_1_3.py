from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
import numpy as np


def calculate_kpi_1_3(
    db      : Session,
    cohorte : int = 2022
) -> Dict[str, Any]:
    """
    KPI 1.3 - Correlación múltiple (R) de predictores de ingreso vs Nota 1er bimestre

    Args:
        db: Sesión de base de datos SQLAlchemy
        cohorte: Año de ingreso de la cohorte (por defecto 2022)

    Returns:
        Dict con «value» (float R), «meta» (dict con R2, coeficientes, etc.)
    """

    # ------ Query: traer predictores + nota B1 desde Gold ------
    query = text("""
        SELECT
            g.id_estudiante,
            g.tipo_prueba,
            g.puntaje_ingreso,
            g.diagnostico,
            g.nota_b1
        FROM gold_kpi_b1_student g
        WHERE g.cohorte = :cohorte
          AND g.puntaje_ingreso IS NOT NULL
          AND g.diagnostico IS NOT NULL
          AND g.nota_b1 IS NOT NULL
        ORDER BY g.id_estudiante
    """)

    # ------ Ejecutar query y cargar a DataFrame ------
    result  = db.execute(query, {"cohorte": cohorte})
    df      = pd.DataFrame(result.fetchall(), columns=[
        'id_estudiante', 'tipo_prueba', 'puntaje_ingreso', 'diagnostico', 'nota_b1'
    ])

    # ------ Validación: mínimo de observaciones para regresión múltiple ------
    if len(df) < 3:
        return {
            "value" : None,
            "meta"  : {
                "cohorte"   : cohorte,
                "n"         : len(df),
                "error"     : "Insuficientes datos para calcular regresión múltiple (se requieren al menos 3 observaciones)"
            }
        }

    # ------ Preparar matrices X (predictores) e y (variable objetivo) ------
    X                   = df[['puntaje_ingreso', 'diagnostico']].values
    y                   = df['nota_b1'].values
    X_with_intercept    = np.column_stack([np.ones(len(X)), X])

    # ------ Ajuste OLS: estimar coeficientes y calcular R2 ------
    try:
        coeffs, residuals, rank, s  = np.linalg.lstsq(X_with_intercept, y, rcond=None)
        beta0                       = coeffs[0]
        beta1                       = coeffs[1]
        beta2                       = coeffs[2]

        y_pred  = X_with_intercept @ coeffs
        ss_res  = float(np.sum((y - y_pred) ** 2))
        ss_tot  = float(np.sum((y - float(np.mean(y))) ** 2))

        r2_raw  = 0.0
        if ss_tot > 0:
            r2_raw = 1.0 - (ss_res / ss_tot)

        # ------ Sanitizar R2 y derivar R = sqrt(R2) ------
        r2_clamped  = max(0.0, min(1.0, r2_raw))
        R           = float(np.sqrt(r2_clamped))

    # ------ Manejo de error numérico (matriz singular / mal condicionada) ------
    except np.linalg.LinAlgError:
        return {
            "value" : None,
            "meta"  : {
                "cohorte"   : cohorte,
                "n"         : len(df),
                "error"     : "Error al calcular regresión múltiple (matriz singular o mal condicionada)"
            }
        }

    # ------ Armar respuesta: valor R + métricas y descriptivos ------
    result_kpi = {
        "value" : float(R),
        "meta"  : {
            "cohorte"       : cohorte,
            "n"             : len(df),
            "R2"            : float(r2_clamped),
            "coeficientes"  : {
                "beta0"             : float(beta0),
                "beta1_paes_pdt"    : float(beta1),
                "beta2_diagnostico" : float(beta2)
            },
            "puntaje_ingreso": {
                "min"       : float(df['puntaje_ingreso'].min()),
                "max"       : float(df['puntaje_ingreso'].max()),
                "promedio"  : float(df['puntaje_ingreso'].mean()),
                "std"       : float(df['puntaje_ingreso'].std())
            },
            "diagnostico": {
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
            },
            "distribucion_tipo_prueba": df['tipo_prueba'].value_counts().to_dict()
        }
    }
    return result_kpi
