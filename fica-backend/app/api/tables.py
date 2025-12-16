"""
API Router para consultar tablas de la base de datos
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import math

from app.core.database.db import get_raw_connection

router = APIRouter()

# Lista de tablas disponibles para consulta
AVAILABLE_TABLES = [
    "estudiantes",
    "semestres",
    "bimestres",
    "asignaturas",
    "rendimiento_ramo",
    "paes",
    "pdt",
    "gold_kpi_b1_student",
    "gold_kpi_student_ramos",
    "gold_kpi_student_aprueba8",
]


@router.get("/database-status")
async def get_database_status():
    """
    Verifica si la base de datos tiene datos.
    Retorna información sobre si se puede ejecutar el ETL.
    """
    try:
        with get_raw_connection() as conn:
            cur = conn.cursor()

            # Verificar si la tabla estudiantes existe
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'estudiantes'
                );
            """)
            table_exists = cur.fetchone()[0]

            if not table_exists:
                # Si la tabla no existe, retornar estado inicial
                cur.close()
                return {
                    "hasData": False,
                    "canRunETL": True,
                    "studentCount": 0,
                    "lastUpload": None,
                }

            # Verificar si hay estudiantes (tabla principal)
            cur.execute("SELECT COUNT(*) FROM estudiantes;")
            student_count = cur.fetchone()[0]

            # Verificar última carga
            cur.execute("""
                SELECT nombre_archivo, fecha_carga 
                FROM carga_csv 
                ORDER BY fecha_carga DESC 
                LIMIT 1;
            """)
            last_upload = cur.fetchone()

            cur.close()

            has_data = student_count > 0

            result = {
                "hasData": has_data,
                "canRunETL": not has_data,  # Solo se puede ejecutar si NO hay datos
                "studentCount": student_count,
                "lastUpload": {
                    "filename": last_upload[0] if last_upload else None,
                    "date": last_upload[1].isoformat() if last_upload else None,
                } if last_upload else None,
            }

            return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar estado de BD: {str(e)}")


@router.get("/tables")
async def get_tables():
    """
    Obtiene la lista de tablas disponibles en la base de datos.
    Solo devuelve tablas que existen Y tienen datos.
    """
    try:
        with get_raw_connection() as conn:
            cur = conn.cursor()

            # Verificar si la tabla estudiantes existe
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'estudiantes'
                );
            """)
            table_exists = cur.fetchone()[0]

            if not table_exists:
                cur.close()
                return {
                    "tables": [],
                    "total": 0,
                    "message": "Las tablas no existen. Debes ejecutar el proceso ETL para cargar los datos."
                }

            # Verificar si la tabla principal (estudiantes) tiene datos
            cur.execute("SELECT COUNT(*) FROM estudiantes;")
            student_count = cur.fetchone()[0]

            # Si no hay estudiantes, no devolver ninguna tabla
            if student_count == 0:
                cur.close()
                return {
                    "tables": [],
                    "total": 0,
                    "message": "Las tablas están vacías. Debes ejecutar el proceso ETL para cargar los datos."
                }

            # Verificar qué tablas realmente existen
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)

            existing_tables = [row[0] for row in cur.fetchall()]
            cur.close()

            # Solo devolver tablas que existen y están en la lista permitida
            tables = [t for t in AVAILABLE_TABLES if t in existing_tables]

            return {
                "tables": tables,
                "total": len(tables)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener tablas: {str(e)}")


@router.get("/tables/{table_name}")
async def get_table_data(
    table_name: str,
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(50, ge=1, le=100, description="Registros por página"),
    search: Optional[str] = Query(None, description="Búsqueda en la tabla")
):
    """
    Obtiene los datos de una tabla específica con paginación
    """
    # Validar que la tabla esté en la lista permitida (seguridad)
    if table_name not in AVAILABLE_TABLES:
        raise HTTPException(status_code=404, detail=f"Tabla '{table_name}' no encontrada")

    try:
        with get_raw_connection() as conn:
            cur = conn.cursor()

            # Verificar que la tabla existe
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table_name,))

            if not cur.fetchone()[0]:
                cur.close()
                raise HTTPException(status_code=404, detail=f"Tabla '{table_name}' no existe en la base de datos")

            # Obtener nombres de columnas
            cur.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position;
            """, (table_name,))

            columns_info = cur.fetchall()
            columns = [col[0] for col in columns_info]

            # Construir query con búsqueda (si se proporciona)
            where_clause = ""
            params = []

            if search and search.strip():
                # Buscar en todas las columnas de tipo texto
                text_columns = [col[0] for col in columns_info if 'char' in col[1].lower() or 'text' in col[1].lower()]
                if text_columns:
                    search_conditions = [f"{col}::text ILIKE %s" for col in text_columns]
                    where_clause = f"WHERE {' OR '.join(search_conditions)}"
                    params = [f"%{search}%" for _ in text_columns]

            # Contar total de registros
            count_query = f"SELECT COUNT(*) FROM {table_name} {where_clause}"
            cur.execute(count_query, params)
            total_records = cur.fetchone()[0]

            # Calcular paginación
            offset = (page - 1) * limit
            total_pages = math.ceil(total_records / limit) if total_records > 0 else 1

            # Obtener datos paginados
            data_query = f"""
                SELECT * FROM {table_name} 
                {where_clause}
                ORDER BY 1
                LIMIT %s OFFSET %s
            """
            cur.execute(data_query, params + [limit, offset])

            rows = cur.fetchall()
            cur.close()

            # Convertir a lista de diccionarios
            data = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Convertir tipos especiales a strings para JSON
                    if value is not None:
                        if hasattr(value, 'isoformat'):  # datetime
                            row_dict[col] = value.isoformat()
                        elif isinstance(value, float):
                            # Handle non-JSON-compliant float values
                            if math.isnan(value) or math.isinf(value):
                                row_dict[col] = None
                            else:
                                row_dict[col] = value
                        else:
                            row_dict[col] = value
                    else:
                        row_dict[col] = None
                data.append(row_dict)

            return {
                "table": table_name,
                "columns": columns,
                "data": data,
                "page": page,
                "limit": limit,
                "totalRecords": total_records,
                "totalPages": total_pages,
                "hasNext": page < total_pages,
                "hasPrev": page > 1
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar tabla: {str(e)}")

