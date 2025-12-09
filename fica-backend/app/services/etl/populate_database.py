import pandas as pd
from psycopg2.extras import execute_values

def clean_numeric(value):
    if pd.isna(value) or value in ("", 0, "0", "0.0") : return None
    if isinstance(value, str) : value = value.replace(",", ".")

    try:
        return float(value)
    except Exception:
        return None

def insert_estudiantes(conn, df: pd.DataFrame) -> int:
    df_valid            = df.dropna(subset=["id_alumno", "año_ingreso", "tipo_ingreso"])
    # Filtrar registros con id_alumno vacío (cadena vacía)
    df_valid            = df_valid[df_valid["id_alumno"] != ""]
    estudiantes         = df_valid[["id_alumno", "año_ingreso", "tipo_ingreso"]].drop_duplicates()
    estudiantes_data    = []
    for _, row in estudiantes.iterrows():
        id_estudiante   = int(row["id_alumno"])
        anio_ingreso    = int(row["año_ingreso"])
        tipo_prueba     = str(row["tipo_ingreso"]).upper()
        student_rows    = df_valid[df_valid["id_alumno"] == row["id_alumno"]].iloc[0]

        if tipo_prueba == "PAES":
            nem     = clean_numeric(student_rows["paes_nem"])
            ranking = clean_numeric(student_rows["paes_ranking"])
        else:
            nem     = clean_numeric(student_rows["pdt_nem"])
            ranking = clean_numeric(student_rows["pdt_ranking"])

        diagnostico = clean_numeric(student_rows["diagnostico_matematica"])

        estudiantes_data.append(
            (id_estudiante, anio_ingreso, tipo_prueba, nem, ranking, diagnostico)
        )

    cur = conn.cursor()
    try:
        execute_values(
            cur,
            """
            INSERT INTO estudiantes (
                id_estudiante,
                anio_ingreso,
                tipo_prueba,
                nem,
                ranking,
                prueba_diagnostico_matematica
            )
            VALUES %s
            ON CONFLICT (id_estudiante) DO NOTHING
            """,
            estudiantes_data,
        )
        conn.commit()
        return len(estudiantes_data)
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()

def insert_semestres(conn, df: pd.DataFrame) -> int:
    df_valid        = df.dropna(subset=["año", "semestre"])
    semestres       = df_valid[["año", "semestre"]].drop_duplicates()
    semestres_data  = [(int(row["año"]), int(row["semestre"])) for _, row in semestres.iterrows()]
    cur             = conn.cursor()

    try:
        execute_values(
            cur,
            """
            INSERT INTO semestres (anio, numero)
            VALUES %s
            ON CONFLICT (anio, numero) DO NOTHING
            """,
            semestres_data,
        )
        conn.commit()
        return len(semestres_data)
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()

def insert_bimestres(conn, df: pd.DataFrame) -> int:
    df_valid        = df.dropna(subset=["año", "semestre", "bimestre"])
    bimestres_df    = df_valid[["año", "semestre", "bimestre"]].drop_duplicates()
    cur             = conn.cursor()
    inserted        = 0
    try:
        for _, row in bimestres_df.iterrows():
            anio      = int(row["año"])
            semestre  = int(row["semestre"])
            bimestre  = int(float(row["bimestre"]))

            cur.execute(
                "SELECT id_semestre FROM semestres WHERE anio = %s AND numero = %s",
                (anio, semestre),
            )
            result = cur.fetchone()
            if not result:
                continue

            id_semestre = result[0]
            cur.execute(
                """
                INSERT INTO bimestres (id_semestre, numero)
                VALUES (%s, %s)
                ON CONFLICT (id_semestre, numero) DO NOTHING
                """,
                (id_semestre, bimestre),
            )

            inserted += 1

        conn.commit()
        return inserted
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()


def insert_asignaturas(conn, df: pd.DataFrame) -> int:
    df_valid            = df.dropna(subset=["codigo_asignatura", "nombre_asignatura"])
    asignaturas         = df_valid[["codigo_asignatura", "modulo", "nombre_asignatura"]].drop_duplicates()
    asignaturas_data    = []

    for _, row in asignaturas.iterrows():
        codigo = row["codigo_asignatura"]
        modulo = str(row["modulo"]) if pd.notna(row["modulo"]) else None
        nombre = row["nombre_asignatura"]
        asignaturas_data.append((codigo, modulo, nombre))

    cur = conn.cursor()
    try:
        execute_values(
            cur,
            """
            INSERT INTO asignaturas (codigo, modulo, nombre)
            VALUES %s
            ON CONFLICT (codigo, modulo, nombre) DO NOTHING
            """,
            asignaturas_data,
        )
        conn.commit()
        return len(asignaturas_data)
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()

def insert_paes(conn, df: pd.DataFrame) -> int:
    df_paes = df[df["tipo_ingreso"].str.upper() == "PAES"].copy()
    df_paes = df_paes.dropna(subset=["id_alumno", "año_ingreso"])
    # Filtrar registros con id_alumno vacío
    df_paes = df_paes[df_paes["id_alumno"] != ""]

    if len(df_paes) == 0 : return 0

    paes_cols = [
        "id_alumno",
        "año_ingreso",
        "paes_comprension_lectora",
        "paes_m1",
        "paes_m2",
        "paes_historia",
        "paes_ciencias",
        "paes_promedio_m1_comprension_lectora",
    ]
    df_paes_unique  = df_paes[paes_cols].drop_duplicates(subset=["id_alumno"])
    paes_data       = []
    for _, row in df_paes_unique.iterrows():
        id_estudiante      = int(row["id_alumno"])
        anio_examen        = int(row["año_ingreso"])
        c_lectora          = clean_numeric(row["paes_comprension_lectora"])
        m1                 = clean_numeric(row["paes_m1"])
        m2                 = clean_numeric(row["paes_m2"])
        historia           = clean_numeric(row["paes_historia"])
        ciencias           = clean_numeric(row["paes_ciencias"])
        prom_m1_clectora   = clean_numeric(row["paes_promedio_m1_comprension_lectora"])

        paes_data.append(
            (id_estudiante, anio_examen, c_lectora, m1, m2, historia, ciencias, prom_m1_clectora)
        )

    cur = conn.cursor()
    try:
        execute_values(
            cur,
            """
            INSERT INTO paes (
                id_estudiante,
                anio_examen,
                c_lectora,
                m1,
                m2,
                historia,
                ciencias,
                prom_m1_clectora
            )
            VALUES %s
            ON CONFLICT (id_estudiante, anio_examen) DO NOTHING
            """,
            paes_data,
        )
        conn.commit()
        return len(paes_data)
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()

def insert_pdt(conn, df: pd.DataFrame) -> int:
    df_pdt = df[df["tipo_ingreso"].str.upper() == "PDT"].copy()
    df_pdt = df_pdt.dropna(subset=["id_alumno", "año_ingreso"])
    # Filtrar registros con id_alumno vacío
    df_pdt = df_pdt[df_pdt["id_alumno"] != ""]

    if len(df_pdt) == 0 : return 0

    pdt_cols = [
        "id_alumno",
        "año_ingreso",
        "pdt_lenguaje",
        "pdt_matematicas",
        "pdt_historia",
        "pdt_ciencias",
        "pdt_promedio_matematicas_lenguaje",
    ]
    df_pdt_unique   = df_pdt[pdt_cols].drop_duplicates(subset=["id_alumno"])
    pdt_data        = []
    for _, row in df_pdt_unique.iterrows():
        id_estudiante  = int(row["id_alumno"])
        anio_examen    = int(row["año_ingreso"])
        lenguaje       = clean_numeric(row["pdt_lenguaje"])
        matematicas    = clean_numeric(row["pdt_matematicas"])
        historia       = clean_numeric(row["pdt_historia"])
        ciencias       = clean_numeric(row["pdt_ciencias"])
        prom_leng_mat  = clean_numeric(row["pdt_promedio_matematicas_lenguaje"])

        pdt_data.append(
            (id_estudiante, anio_examen, lenguaje, matematicas, historia, ciencias, prom_leng_mat)
        )

    cur = conn.cursor()
    try:
        execute_values(
            cur,
            """
            INSERT INTO pdt (
                id_estudiante,
                anio_examen,
                lenguaje,
                matematicas,
                historia,
                ciencias,
                prom_leng_mat
            )
            VALUES %s
            ON CONFLICT (id_estudiante, anio_examen) DO NOTHING
            """,
            pdt_data,
        )
        conn.commit()
        return len(pdt_data)
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()

def insert_rendimiento_ramo(conn, df: pd.DataFrame) -> int:
    cur             = conn.cursor()
    inserted_count  = 0
    df_valid        = df.dropna(
        subset=[
            "id_alumno",
            "año",
            "semestre",
            "bimestre",
            "codigo_asignatura",
            "nombre_asignatura",
        ]
    )
    # Filtrar registros con id_alumno vacío
    df_valid = df_valid[df_valid["id_alumno"] != ""]

    try:
        for _, row in df_valid.iterrows():
            id_estudiante     = int(row["id_alumno"])
            anio              = int(row["año"])
            semestre          = int(row["semestre"])
            bimestre          = int(float(row["bimestre"]))
            codigo_asignatura = row["codigo_asignatura"]
            modulo            = str(row["modulo"]) if pd.notna(row["modulo"]) else None
            nombre_asignatura = row["nombre_asignatura"]
            nota_final        = clean_numeric(row["nota_final"])
            estado_final      = row["estado_final"] if pd.notna(row["estado_final"]) else None

            # id_semestre
            cur.execute(
                "SELECT id_semestre FROM semestres WHERE anio = %s AND numero = %s",
                (anio, semestre),
            )
            result = cur.fetchone()
            if not result : continue
            id_semestre = result[0]

            # id_bimestre
            cur.execute(
                "SELECT id_bimestre FROM bimestres WHERE id_semestre = %s AND numero = %s",
                (id_semestre, bimestre),
            )
            result = cur.fetchone()
            if not result : continue
            id_bimestre = result[0]

            # id_asignatura
            cur.execute(
                """
                SELECT id_asignatura
                FROM asignaturas
                WHERE codigo = %s
                  AND (modulo = %s OR (modulo IS NULL AND %s IS NULL))
                  AND nombre = %s
                """,
                (codigo_asignatura, modulo, modulo, nombre_asignatura),
            )
            result = cur.fetchone()
            if not result : continue
            id_asignatura = result[0]

            # Insert rendimiento
            cur.execute(
                """
                INSERT INTO rendimiento_ramo (
                    id_estudiante,
                    id_bimestre,
                    id_asignatura,
                    nota_final,
                    estado_final
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id_estudiante, id_bimestre, id_asignatura) DO NOTHING
                """,
                (id_estudiante, id_bimestre, id_asignatura, nota_final, estado_final),
            )

            inserted_count += 1

            if inserted_count % 100 == 0:
                conn.commit()

        conn.commit()
        return inserted_count
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()

def populate_all(conn, df: pd.DataFrame) -> dict:
    summary = {}

    summary["estudiantes"] = insert_estudiantes(conn, df)
    summary["semestres"]   = insert_semestres(conn, df)
    summary["bimestres"]   = insert_bimestres(conn, df)
    summary["asignaturas"] = insert_asignaturas(conn, df)
    summary["paes"]        = insert_paes(conn, df)
    summary["pdt"]         = insert_pdt(conn, df)
    summary["rendimiento"] = insert_rendimiento_ramo(conn, df)
    return summary
