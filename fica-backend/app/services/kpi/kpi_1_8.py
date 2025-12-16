from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd


def calculate_kpi_1_8(
    db      : Session,
    cohorte : int = 2022
) -> Dict[str, Any]:
    """
    KPI 1.8 - Tasa de reprobación Nota 1er bimestre por quintil

    Args:
        db      : Sesión de base de datos SQLAlchemy
        cohorte : Año de ingreso de la cohorte (por defecto 2022)

    Returns:
        Dict con «value» (dict con Q1..Q5), «meta» (dict con detalles, etc.)
    """

    # ------ Query: traer predictores + NotaB1 desde Gold (cohorte) ------
    query = text("""
        SELECT
            id_estudiante,
            puntaje_ingreso,
            diagnostico,
            nota_b1
        FROM gold_kpi_b1_student
        WHERE cohorte = :cohorte
    """)

    # ------ Ejecutar query y armar DataFrame ------
    result  = db.execute(query, {"cohorte": cohorte})
    df      = pd.DataFrame(result.fetchall(), columns=[
        "id_estudiante", "puntaje_ingreso", "diagnostico", "nota_b1"
    ])

    # ------ Validación: sin datos para la cohorte ------
    if len(df) == 0:
        return {
            "value" : None,
            "meta"  : {
                "cohorte"   : cohorte,
                "n_total"   : 0,
                "error"     : "No se encontraron estudiantes para la cohorte especificada (tabla Gold vacía)"
            }
        }

    # ------ Construir índice de ingreso (regla operacional) ------
    def calcular_indice_ingreso(row):
        puntaje_ingreso = row["puntaje_ingreso"]
        diagnostico     = row["diagnostico"]

        if pd.notna(puntaje_ingreso) and pd.notna(diagnostico):
            return (puntaje_ingreso + diagnostico) / 2.0
        if pd.notna(puntaje_ingreso):
            return puntaje_ingreso
        if pd.notna(diagnostico):
            return diagnostico
        return None

    df["indice_ingreso"] = df.apply(calcular_indice_ingreso, axis=1)

    # ------ Filtrar estudiantes válidos (índice + nota_b1) ------
    df_validos = df[
        (df["indice_ingreso"].notna()) &
        (df["nota_b1"].notna())
    ].copy()

    # ------ Conteos base (total, válidos, excluidos) ------
    n_total     = int(len(df))
    n_validos   = int(len(df_validos))
    n_excluidos = int(n_total - n_validos)

    # ------ Validación: mínimo de observaciones para quintiles ------
    if n_validos < 5:
        return {
            "value" : None,
            "meta"  : {
                "cohorte"       : cohorte,
                "n_total"       : n_total,
                "n_validos"     : n_validos,
                "n_excluidos"   : n_excluidos,
                "error"         : "Insuficientes estudiantes con índice de ingreso y NotaB1 válidos para calcular quintiles (se requieren al menos 5)"
            }
        }

    # ------ Validación: suficientes valores distintos para 5 cortes ------
    cantidad_valores_distintos = int(df_validos["indice_ingreso"].nunique())
    if cantidad_valores_distintos < 5:
        return {
            "value" : None,
            "meta"  : {
                "cohorte"                   : cohorte,
                "n_total"                   : n_total,
                "n_validos"                 : n_validos,
                "n_excluidos"               : n_excluidos,
                "valores_distintos_indice"  : cantidad_valores_distintos,
                "error"                     : "No hay suficientes valores distintos del índice para formar 5 quintiles"
            }
        }

    # ------ Construir quintiles (Q1..Q5) según el índice ------
    try:
        df_validos["quintil"] = pd.qcut(
            df_validos["indice_ingreso"],
            q       = 5,
            labels  = ["Q1", "Q2", "Q3", "Q4", "Q5"]
        )
    except ValueError:
        return {
            "value" : None,
            "meta"  : {
                "cohorte"       : cohorte,
                "n_total"       : n_total,
                "n_validos"     : n_validos,
                "n_excluidos"   : n_excluidos,
                "error"         : "No se pudieron construir quintiles (posibles cortes duplicados en el índice)"
            }
        }

    # ------ Calcular tasa de reprobación (<4.0) por quintil + detalles ------
    tasas               = {}
    detalles_quintiles  = {}

    for quintil in ["Q1", "Q2", "Q3", "Q4", "Q5"]:
        df_quintil  = df_validos[df_validos["quintil"] == quintil]
        n_total_k   = int(len(df_quintil))

        if n_total_k > 0:
            n_reprobados_k  = int((df_quintil["nota_b1"] < 4.0).sum())
            tasa_k          = float((n_reprobados_k / n_total_k) * 100)

            tasas[quintil] = float(tasa_k)
            detalles_quintiles[quintil] = {
                "n_total"           : n_total_k,
                "n_reprobados"      : n_reprobados_k,
                "n_aprobados"       : int(n_total_k - n_reprobados_k),
                "tasa_reprobacion"  : float(tasa_k)
            }
        else:
            tasas[quintil]              = None
            detalles_quintiles[quintil] = {"n_total": 0}

    # ------ Notas: decisiones operacionales y exclusiones ------
    notes = [
        "El índice de ingreso se operacionaliza como promedio(PuntajeIngreso, Diagnóstico) si ambos existen; si no, usa el disponible."
    ]
    if n_excluidos > 0:
        notes.append(
            f"{n_excluidos} estudiantes fueron excluidos por no tener índice de ingreso o NotaB1 disponible"
        )

    # ------ Armar respuesta final del KPI ------
    result_kpi = {
        "value" : tasas,
        "meta"  : {
            "cohorte"               : cohorte,
            "n_total"               : n_total,
            "n_validos"             : n_validos,
            "n_excluidos"           : n_excluidos,
            "detalles_quintiles"    : detalles_quintiles,
            "notes"                 : notes
        }
    }
    return result_kpi
