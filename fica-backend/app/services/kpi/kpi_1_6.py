from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd


def calculate_kpi_1_6(
    db      : Session,
    cohorte : int = 2022
) -> Dict[str, Any]:
    """
    KPI 1.6 - Distribución por quintiles del perfil de ingreso

    Args:
        db      : Sesión de base de datos SQLAlchemy
        cohorte : Año de ingreso de la cohorte (por defecto 2022)

    Returns:
        Dict con «value» (dict con Q1..Q5), «meta» (dict con E, detalles, etc.)
    """

    # ------ Query: traer predictores desde Gold (cohorte) ------
    query = text("""
        SELECT
            id_estudiante,
            puntaje_ingreso,
            diagnostico
        FROM gold_kpi_b1_student
        WHERE cohorte = :cohorte
    """)

    # ------ Ejecutar query y armar DataFrame ------
    result  = db.execute(query, {"cohorte": cohorte})
    df      = pd.DataFrame(result.fetchall(), columns=[
        "id_estudiante", "puntaje_ingreso", "diagnostico"
    ])

    # ------ Validación: sin datos para la cohorte ------
    if len(df) == 0:
        return {
            "value" : None,
            "meta"  : {
                "cohorte"   : cohorte,
                "E"         : 0,
                "error"     : "No se encontraron estudiantes para la cohorte especificada (tabla Gold vacía)"
            }
        }

    # ------ Conteos base (total y luego válidos) ------
    E_total = len(df)

    # ------ Construir índice de ingreso (regla operacional) ------
    def calcular_indice_ingreso(row):
        puntaje_ingreso = row["puntaje_ingreso"]
        diagnostico     = row["diagnostico"]

        if pd.notna(puntaje_ingreso) and pd.notna(diagnostico):
            indice_ingreso = (puntaje_ingreso + diagnostico) / 2.0
            return indice_ingreso
        if pd.notna(puntaje_ingreso):
            indice_ingreso = puntaje_ingreso
            return indice_ingreso
        if pd.notna(diagnostico):
            indice_ingreso = diagnostico
            return indice_ingreso
        return None

    df["indice_ingreso"]    = df.apply(calcular_indice_ingreso, axis=1)

    # ------ Filtrar estudiantes con índice válido ------
    df_validos      = df[df["indice_ingreso"].notna()].copy()
    E_validos       = len(df_validos)
    E_excluidos     = E_total - E_validos

    # ------ Validación: mínimo de observaciones para quintiles ------
    if E_validos < 5:
        return {
            "value" : None,
            "meta"  : {
                "cohorte"       : cohorte,
                "E"             : E_validos,
                "E_total"       : E_total,
                "E_excluidos"   : E_excluidos,
                "error"         : "Insuficientes estudiantes con índice de ingreso válido para calcular quintiles (se requieren al menos 5)"
            }
        }

    # ------ Validación: suficientes valores distintos para 5 cortes ------
    cantidad_valores_distintos = int(df_validos["indice_ingreso"].nunique())
    if cantidad_valores_distintos < 5:
        return {
            "value" : None,
            "meta"  : {
                "cohorte"                   : cohorte,
                "E"                         : E_validos,
                "E_total"                   : E_total,
                "E_excluidos"               : E_excluidos,
                "valores_distintos_indice"  : cantidad_valores_distintos,
                "error"                     : "No hay suficientes valores distintos del índice para formar 5 quintiles"
            }
        }

    # ------ Construir quintiles (Q1..Q5) según el índice ------
    df_validos["quintil"] = pd.qcut(
        df_validos["indice_ingreso"],
        q       = 5,
        labels  = ["Q1", "Q2", "Q3", "Q4", "Q5"]
    )

    # ------ Distribución absoluta por quintil ------
    distribucion_absoluta = df_validos["quintil"].value_counts().sort_index()

    # ------ Convertir a porcentajes por quintil ------
    porcentajes = {}
    for quintil in ["Q1", "Q2", "Q3", "Q4", "Q5"]:
        cantidad_en_quintil      = int(distribucion_absoluta.get(quintil, 0))
        porcentaje_en_quintil    = float((cantidad_en_quintil / E_validos) * 100) if E_validos > 0 else 0.0
        porcentajes[quintil]     = porcentaje_en_quintil

    # ------ Notas: decisiones operacionales y exclusiones ------
    notes = []
    notes.append(
        "El índice de ingreso se operacionaliza como promedio(PuntajeIngreso, Diagnóstico) si ambos existen; si no, usa el disponible."
    )
    if E_excluidos > 0:
        notes.append(
            f"{E_excluidos} estudiantes fueron excluidos por no tener PuntajeIngreso ni Diagnóstico disponible"
        )

    # ------ Armar respuesta final del KPI ------
    result_kpi = {
        "value" : porcentajes,
        "meta"  : {
            "cohorte"               : cohorte,
            "E"                     : E_validos,
            "E_total"               : E_total,
            "E_excluidos"           : E_excluidos,
            "distribucion_absoluta" : {k: int(v) for k, v in distribucion_absoluta.to_dict().items()},
            "indice_ingreso"        : {
                "min"       : float(df_validos["indice_ingreso"].min()),
                "max"       : float(df_validos["indice_ingreso"].max()),
                "promedio"  : float(df_validos["indice_ingreso"].mean()),
                "mediana"   : float(df_validos["indice_ingreso"].median()),
                "std"       : float(df_validos["indice_ingreso"].std())
            },
            "notes" : notes
        }
    }
    return result_kpi
