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
          AND g.nota_b1 IS NOT NULL
        ORDER BY g.id_estudiante
    """)

    # ------ Ejecutar query y cargar a DataFrame ------
    result  = db.execute(query, {"cohorte": cohorte})
    df      = pd.DataFrame(result.fetchall(), columns=[
        'id_estudiante', 'tipo_prueba', 'puntaje_ingreso', 'diagnostico', 'nota_b1'
    ])

    # ------ Limpiar datos: remover cualquier NaN/NULL restante ------
    df = df.dropna(subset=['puntaje_ingreso', 'nota_b1'])

    # ------ Validación: mínimo de observaciones para regresión ------
    if len(df) < 3:
        return {
            "value" : None,
            "meta"  : {
                "cohorte"   : cohorte,
                "n"         : len(df),
                "error"     : "Insuficientes datos para calcular regresión (se requieren al menos 3 observaciones)"
            }
        }

    # ------ Determinar qué predictores están disponibles ------
    df['diagnostico_valido'] = df['diagnostico'].notna()
    n_con_diagnostico = df['diagnostico_valido'].sum()

    # Si tenemos suficientes datos de diagnóstico, usamos regresión múltiple
    usar_regresion_multiple = n_con_diagnostico >= 3

    # ------ Preparar matrices X (predictores) e y (variable objetivo) ------
    y = df['nota_b1'].values

    if usar_regresion_multiple:
        # Filtrar solo registros con diagnóstico válido
        df_valid = df[df['diagnostico_valido']].copy()
        X = df_valid[['puntaje_ingreso', 'diagnostico']].values
        y = df_valid['nota_b1'].values
        X_with_intercept = np.column_stack([np.ones(len(X)), X])
        tipo_regresion = "múltiple"
        predictores = ["puntaje_ingreso", "diagnostico"]
    else:
        # Regresión simple solo con puntaje_ingreso
        X = df[['puntaje_ingreso']].values
        X_with_intercept = np.column_stack([np.ones(len(X)), X])
        tipo_regresion = "simple"
        predictores = ["puntaje_ingreso"]

    # ------ Ajuste OLS: estimar coeficientes y calcular R2 ------
    try:
        coeffs, residuals, rank, s = np.linalg.lstsq(X_with_intercept, y, rcond=None)

        # Verificar que los coeficientes sean válidos
        if np.any(np.isnan(coeffs)) or np.any(np.isinf(coeffs)):
            raise ValueError("Coeficientes contienen valores NaN o infinitos")

        beta0 = coeffs[0]
        beta1 = coeffs[1]
        beta2 = coeffs[2] if len(coeffs) > 2 else None

        y_pred = X_with_intercept @ coeffs
        ss_res = float(np.sum((y - y_pred) ** 2))
        ss_tot = float(np.sum((y - float(np.mean(y))) ** 2))

        r2_raw = 0.0
        if ss_tot > 0:
            r2_raw = 1.0 - (ss_res / ss_tot)

        # ------ Sanitizar R2 y derivar R = sqrt(R2) ------
        r2_clamped = max(0.0, min(1.0, r2_raw))
        R = float(np.sqrt(r2_clamped))

    # ------ Manejo de error numérico (matriz singular / mal condicionada) ------
    except (np.linalg.LinAlgError, ValueError) as e:
        return {
            "value" : None,
            "meta"  : {
                "cohorte"   : cohorte,
                "n"         : len(df),
                "error"     : f"Error al calcular regresión: {str(e)}"
            }
        }

    # ------ Armar respuesta: valor R + métricas y descriptivos ------
    coeficientes_dict = {
        "beta0": float(beta0),
        "beta1_paes_pdt": float(beta1)
    }
    if beta2 is not None:
        coeficientes_dict["beta2_diagnostico"] = float(beta2)

    result_kpi = {
        "value" : float(R),
        "meta"  : {
            "cohorte"       : cohorte,
            "n"             : len(y),
            "n_total"       : len(df),
            "tipo_regresion": tipo_regresion,
            "predictores"   : predictores,
            "R2"            : float(r2_clamped),
            "coeficientes"  : coeficientes_dict,
            "puntaje_ingreso": {
                "min"       : float(df['puntaje_ingreso'].min()),
                "max"       : float(df['puntaje_ingreso'].max()),
                "promedio"  : float(df['puntaje_ingreso'].mean()),
                "std"       : float(df['puntaje_ingreso'].std())
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

    # Agregar estadísticas de diagnóstico solo si están disponibles
    if usar_regresion_multiple:
        df_valid_diagnostico = df[df['diagnostico_valido']]
        result_kpi["meta"]["diagnostico"] = {
            "min"       : float(df_valid_diagnostico['diagnostico'].min()),
            "max"       : float(df_valid_diagnostico['diagnostico'].max()),
            "promedio"  : float(df_valid_diagnostico['diagnostico'].mean()),
            "std"       : float(df_valid_diagnostico['diagnostico'].std())
        }
    else:
        result_kpi["meta"]["notes"] = [
            "No hay suficientes datos de diagnóstico. Se utilizó regresión simple solo con puntaje de ingreso."
        ]

    return result_kpi
