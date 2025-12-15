from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text


def calculate_kpi_1_5(
    db      : Session,
    cohorte : int = 2022
) -> Dict[str, Any]:
    """
    KPI 1.5 - Tasa de deserción / congelamiento (no completan 8 ramos)

    Args:
        db: Sesión de base de datos SQLAlchemy
        cohorte: Año de ingreso de la cohorte (por defecto 2022)

    Returns:
        Dict con «value» (float %), «meta» (dict con E, N_no_completan, N_completan)
    """

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

    # ------ Query: contar quienes NO completan 8 ramos y cobertura en Gold ------
    query_no_completan = text("""
        SELECT
            COUNT(*) FILTER (WHERE total_ramos < 8) AS N_no_completan,
            COUNT(*)                                AS E_con_datos
        FROM gold_kpi_student_ramos
        WHERE cohorte = :cohorte
    """)

    # ------ Ejecutar query de no completan y extraer métricas ------
    result_no_completan  = db.execute(query_no_completan, {"cohorte": cohorte})
    row_no_completan     = result_no_completan.fetchone()

    N_no_completan  = 0
    E_con_datos     = 0
    if row_no_completan:
        N_no_completan  = int(row_no_completan[0]) if row_no_completan[0] is not None else 0
        E_con_datos     = int(row_no_completan[1]) if row_no_completan[1] is not None else 0

    # ------ Calcular totales derivados y tasa de deserción ------
    N_completan     = E - N_no_completan
    tasa_desercion  = float((N_no_completan / E) * 100) if E > 0 else 0.0

    # ------ Notas de calidad de datos (cobertura Gold vs cohorte) ------
    notes = []
    if E_con_datos < E:
        notes.append(
            f"{E - E_con_datos} estudiantes no pudieron evaluarse en Gold (faltan registros para total_ramos)"
        )

    # ------ Armar respuesta final del KPI ------
    result_kpi = {
        "value" : float(tasa_desercion),
        "meta"  : {
            "cohorte"        : cohorte,
            "E"              : E,
            "E_con_datos"    : E_con_datos,
            "N_no_completan" : int(N_no_completan),
            "N_completan"    : int(N_completan),
            "notes"          : notes if notes else None
        }
    }
    return result_kpi
