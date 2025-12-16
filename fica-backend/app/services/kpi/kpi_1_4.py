from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text


def calculate_kpi_1_4(
    db      : Session,
    cohorte : int = 2022
) -> Dict[str, Any]:
    """
    KPI 1.4 - Estudiantes que aprueban los 8 bimestres sin reprobar ramos

    Args:
        db      : Sesión de base de datos SQLAlchemy
        cohorte : Año de ingreso de la cohorte (por defecto 2022). Este KPI solo
                  está definido operacionalmente para la cohorte 2022, ya que el
                  dataset actual (2022–2024) solo garantiza 8 bimestres completos
                  para ese año de ingreso.

    Returns:
        Dict con «value» (int), «meta» (dict con E, detalles, etc.)
    """

    # ------ Restricción operacional: solo cohorte 2022 ------
    if cohorte != 2022:
        return {
            "value": None,
            "meta": {
                "cohorte"   : cohorte,
                "E"         : 0,
                "error"     : "KPI 1.4 solo está definido para la cohorte 2022 (dataset 2022–2024).",
            },
        }

    # ------ Query: total de estudiantes de la cohorte ------
    query_total_estudiantes = text("""
        SELECT COUNT(*) AS E
        FROM estudiantes
        WHERE anio_ingreso = :cohorte
    """)

    # ------ Ejecutar query total y validar cohorte ------
    result_total_estudiantes = db.execute(query_total_estudiantes, {"cohorte": cohorte})
    row_total_estudiantes    = result_total_estudiantes.fetchone()

    E = int(row_total_estudiantes[0]) if row_total_estudiantes else 0
    if E == 0:
        return {
            "value" : None,
            "meta"  : {
                "cohorte"   : cohorte,
                "E"         : 0,
                "error"     : "No se encontraron estudiantes para la cohorte especificada"
            }
        }

    # ------ Query: contar quienes aprueban_8 (True) y cuántos tienen datos en Gold ------
    query_aprueba8 = text("""
        SELECT
            COUNT(*) FILTER (WHERE aprueba_8 = TRUE) AS Naprueban_8,
            COUNT(*)                              AS E_con_datos
        FROM gold_kpi_student_aprueba8
        WHERE cohorte = :cohorte
    """)

    # ------ Ejecutar query de aprobación y extraer métricas ------
    result_aprueba8 = db.execute(query_aprueba8, {"cohorte": cohorte})
    row_aprueba8    = result_aprueba8.fetchone()

    Naprueban_8 = 0
    E_con_datos = 0
    if row_aprueba8:
        Naprueban_8 = int(row_aprueba8[0]) if row_aprueba8[0] is not None else 0
        E_con_datos = int(row_aprueba8[1]) if row_aprueba8[1] is not None else 0

    # ------ Calcular tasa de aprobación (referencia: total cohorte) ------
    tasa_aprobacion = float((Naprueban_8 / E) * 100) if E > 0 else 0.0

    # ------ Notas de calidad de datos (cobertura Gold vs cohorte) ------
    notes = []
    if E_con_datos < E:
        notes.append(
            f"{E - E_con_datos} estudiantes no pudieron evaluarse en Gold (faltan registros para aprueba_8)"
        )

    # ------ Armar respuesta final del KPI ------
    result_kpi = {
        "value" : Naprueban_8,
        "meta"  : {
            "cohorte"           : cohorte,
            "E"                 : E,
            "E_con_datos"       : E_con_datos,
            "Naprueban_8"       : Naprueban_8,
            "tasa_aprobacion"   : tasa_aprobacion,
            "notes"             : notes if notes else None
        }
    }
    return result_kpi
