import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import sys
from db_config import DB_CONFIG


def connect_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✓ Conexión exitosa a la base de datos")
        return conn
    except Exception as e:
        print(f"✗ Error al conectar a la base de datos: {e}")
        sys.exit(1)


def load_csv():
    try:
        df = pd.read_csv('../data/3.fica_bimestres_grouped_by_student.csv')

        print(f"✓ CSV cargado exitosamente: {len(df)} registros")
        print(f"✓ Columnas detectadas: {', '.join(df.columns[:5])}...")
        return df
    except Exception as e:
        print(f"✗ Error al cargar el CSV: {e}")
        sys.exit(1)


def clean_numeric(value):
    if pd.isna(value) or value == '' or value == 0 or value == '0' or value == '0.0':
        return None
    if isinstance(value, str):
        value = value.replace(',', '.')
    try:
        return float(value)
    except:
        return None


def insert_estudiantes(conn, df):
    print("\n→ Insertando estudiantes...")

    df_valid = df.dropna(subset=['id_alumno', 'año_ingreso', 'tipo_ingreso'])

    estudiantes = df_valid[['id_alumno', 'año_ingreso', 'tipo_ingreso']].drop_duplicates()

    estudiantes_data = []
    for _, row in estudiantes.iterrows():
        id_estudiante = int(row['id_alumno'])
        anio_ingreso = int(row['año_ingreso'])
        tipo_prueba = row['tipo_ingreso'].upper()

        student_rows = df_valid[df_valid['id_alumno'] == row['id_alumno']].iloc[0]

        if tipo_prueba == 'PAES':
            nem = clean_numeric(student_rows['paes_nem'])
            ranking = clean_numeric(student_rows['paes_ranking'])
        else:
            nem = clean_numeric(student_rows['pdt_nem'])
            ranking = clean_numeric(student_rows['pdt_ranking'])

        diagnostico = clean_numeric(student_rows['diagnostico_matematica'])

        estudiantes_data.append((id_estudiante, anio_ingreso, tipo_prueba, nem, ranking, diagnostico))

    cur = conn.cursor()
    try:
        execute_values(
            cur,
            """
            INSERT INTO estudiantes (id_estudiante, anio_ingreso, tipo_prueba, nem, ranking, prueba_diagnostico_matematica)
            VALUES %s
            ON CONFLICT (id_estudiante) DO NOTHING
            """,
            estudiantes_data
        )
        conn.commit()
        print(f"✓ {len(estudiantes_data)} estudiantes insertados")
    except Exception as e:
        conn.rollback()
        print(f"✗ Error al insertar estudiantes: {e}")
        raise
    finally:
        cur.close()


def insert_semestres(conn, df):
    print("\n→ Insertando semestres...")

    df_valid = df.dropna(subset=['año', 'semestre'])
    semestres = df_valid[['año', 'semestre']].drop_duplicates()
    semestres_data = [(int(row['año']), int(row['semestre'])) for _, row in semestres.iterrows()]

    cur = conn.cursor()
    try:
        execute_values(
            cur,
            """
            INSERT INTO semestres (anio, numero)
            VALUES %s
            ON CONFLICT (anio, numero) DO NOTHING
            """,
            semestres_data
        )
        conn.commit()
        print(f"✓ {len(semestres_data)} semestres insertados")
    except Exception as e:
        conn.rollback()
        print(f"✗ Error al insertar semestres: {e}")
        raise
    finally:
        cur.close()


def insert_bimestres(conn, df):
    print("\n→ Insertando bimestres...")

    df_valid = df.dropna(subset=['año', 'semestre', 'bimestre'])
    bimestres_df = df_valid[['año', 'semestre', 'bimestre']].drop_duplicates()

    cur = conn.cursor()
    try:
        for _, row in bimestres_df.iterrows():
            anio = int(row['año'])
            semestre = int(row['semestre'])
            bimestre = int(float(row['bimestre']))

            cur.execute(
                "SELECT id_semestre FROM semestres WHERE anio = %s AND numero = %s",
                (anio, semestre)
            )
            id_semestre = cur.fetchone()[0]

            cur.execute(
                """
                INSERT INTO bimestres (id_semestre, numero)
                VALUES (%s, %s)
                ON CONFLICT (id_semestre, numero) DO NOTHING
                """,
                (id_semestre, bimestre)
            )

        conn.commit()
        print(f"✓ Bimestres insertados")
    except Exception as e:
        conn.rollback()
        print(f"✗ Error al insertar bimestres: {e}")
        raise
    finally:
        cur.close()


def insert_asignaturas(conn, df):
    print("\n→ Insertando asignaturas...")

    df_valid = df.dropna(subset=['codigo_asignatura', 'nombre_asignatura'])
    asignaturas = df_valid[['codigo_asignatura', 'modulo', 'nombre_asignatura']].drop_duplicates()
    asignaturas_data = []

    for _, row in asignaturas.iterrows():
        codigo = row['codigo_asignatura']
        modulo = str(row['modulo']) if pd.notna(row['modulo']) else None
        nombre = row['nombre_asignatura']
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
            asignaturas_data
        )
        conn.commit()
        print(f"✓ {len(asignaturas_data)} asignaturas insertadas")
    except Exception as e:
        conn.rollback()
        print(f"✗ Error al insertar asignaturas: {e}")
        raise
    finally:
        cur.close()


def insert_paes(conn, df):
    print("\n→ Insertando registros PAES...")

    df_paes = df[df['tipo_ingreso'].str.upper() == 'PAES'].copy()
    df_paes = df_paes.dropna(subset=['id_alumno', 'año_ingreso'])

    if len(df_paes) == 0:
        print("  No hay registros PAES en el dataset")
        return

    paes_cols = ['id_alumno', 'año_ingreso', 'paes_comprension_lectora', 'paes_m1', 'paes_m2',
                 'paes_historia', 'paes_ciencias', 'paes_promedio_m1_comprension_lectora']
    df_paes_unique = df_paes[paes_cols].drop_duplicates(subset=['id_alumno'])

    paes_data = []
    for _, row in df_paes_unique.iterrows():
        id_estudiante = int(row['id_alumno'])
        anio_examen = int(row['año_ingreso'])
        c_lectora = clean_numeric(row['paes_comprension_lectora'])
        m1 = clean_numeric(row['paes_m1'])
        m2 = clean_numeric(row['paes_m2'])
        historia = clean_numeric(row['paes_historia'])
        ciencias = clean_numeric(row['paes_ciencias'])
        prom_m1_clectora = clean_numeric(row['paes_promedio_m1_comprension_lectora'])

        paes_data.append((id_estudiante, anio_examen, c_lectora, m1, m2, historia, ciencias, prom_m1_clectora))

    cur = conn.cursor()
    try:
        execute_values(
            cur,
            """
            INSERT INTO paes (id_estudiante, anio_examen, c_lectora, m1, m2, historia, ciencias, prom_m1_clectora)
            VALUES %s
            ON CONFLICT (id_estudiante, anio_examen) DO NOTHING
            """,
            paes_data
        )
        conn.commit()
        print(f"✓ {len(paes_data)} registros PAES insertados")
    except Exception as e:
        conn.rollback()
        print(f"✗ Error al insertar registros PAES: {e}")
        raise
    finally:
        cur.close()


def insert_pdt(conn, df):
    print("\n→ Insertando registros PDT...")

    df_pdt = df[df['tipo_ingreso'].str.upper() == 'PDT'].copy()
    df_pdt = df_pdt.dropna(subset=['id_alumno', 'año_ingreso'])

    if len(df_pdt) == 0:
        print("  No hay registros PDT en el dataset")
        return

    pdt_cols = ['id_alumno', 'año_ingreso', 'pdt_lenguaje', 'pdt_matematicas',
                'pdt_historia', 'pdt_ciencias', 'pdt_promedio_matematicas_lenguaje']
    df_pdt_unique = df_pdt[pdt_cols].drop_duplicates(subset=['id_alumno'])

    pdt_data = []
    for _, row in df_pdt_unique.iterrows():
        id_estudiante = int(row['id_alumno'])
        anio_examen = int(row['año_ingreso'])
        lenguaje = clean_numeric(row['pdt_lenguaje'])
        matematicas = clean_numeric(row['pdt_matematicas'])
        historia = clean_numeric(row['pdt_historia'])
        ciencias = clean_numeric(row['pdt_ciencias'])
        prom_leng_mat = clean_numeric(row['pdt_promedio_matematicas_lenguaje'])

        pdt_data.append((id_estudiante, anio_examen, lenguaje, matematicas, historia, ciencias, prom_leng_mat))

    cur = conn.cursor()
    try:
        execute_values(
            cur,
            """
            INSERT INTO pdt (id_estudiante, anio_examen, lenguaje, matematicas, historia, ciencias, prom_leng_mat)
            VALUES %s
            ON CONFLICT (id_estudiante, anio_examen) DO NOTHING
            """,
            pdt_data
        )
        conn.commit()
        print(f"✓ {len(pdt_data)} registros PDT insertados")
    except Exception as e:
        conn.rollback()
        print(f"✗ Error al insertar registros PDT: {e}")
        raise
    finally:
        cur.close()


def insert_rendimiento_ramo(conn, df):
    print("\n→ Insertando rendimiento de ramos...")

    cur = conn.cursor()
    inserted_count = 0

    df_valid = df.dropna(subset=['id_alumno', 'año', 'semestre', 'bimestre', 'codigo_asignatura', 'nombre_asignatura'])

    try:
        for idx, row in df_valid.iterrows():
            id_estudiante = int(row['id_alumno'])
            anio = int(row['año'])
            semestre = int(row['semestre'])
            bimestre = int(float(row['bimestre']))
            codigo_asignatura = row['codigo_asignatura']
            modulo = str(row['modulo']) if pd.notna(row['modulo']) else None
            nombre_asignatura = row['nombre_asignatura']
            nota_final = clean_numeric(row['nota_final'])
            estado_final = row['estado_final'] if pd.notna(row['estado_final']) else None

            cur.execute(
                "SELECT id_semestre FROM semestres WHERE anio = %s AND numero = %s",
                (anio, semestre)
            )
            result = cur.fetchone()
            if not result:
                print(f"  Advertencia: No se encontró semestre para año={anio}, semestre={semestre}")
                continue
            id_semestre = result[0]

            cur.execute(
                "SELECT id_bimestre FROM bimestres WHERE id_semestre = %s AND numero = %s",
                (id_semestre, bimestre)
            )
            result = cur.fetchone()
            if not result:
                print(f"  Advertencia: No se encontró bimestre para semestre={id_semestre}, bimestre={bimestre}")
                continue
            id_bimestre = result[0]

            cur.execute(
                """
                SELECT id_asignatura FROM asignaturas 
                WHERE codigo = %s AND (modulo = %s OR (modulo IS NULL AND %s IS NULL)) AND nombre = %s
                """,
                (codigo_asignatura, modulo, modulo, nombre_asignatura)
            )
            result = cur.fetchone()
            if not result:
                print(f"  Advertencia: No se encontró asignatura {codigo_asignatura}")
                continue
            id_asignatura = result[0]

            cur.execute(
                """
                INSERT INTO rendimiento_ramo (id_estudiante, id_bimestre, id_asignatura, nota_final, estado_final)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id_estudiante, id_bimestre, id_asignatura) DO NOTHING
                """,
                (id_estudiante, id_bimestre, id_asignatura, nota_final, estado_final)
            )

            inserted_count += 1

            if inserted_count % 100 == 0:
                conn.commit()
                print(f"  Procesados {inserted_count}/{len(df_valid)} registros...")

        conn.commit()
        print(f"✓ {inserted_count} registros de rendimiento insertados")
    except Exception as e:
        conn.rollback()
        print(f"✗ Error al insertar rendimiento: {e}")
        raise
    finally:
        cur.close()


def main():
    print("=" * 60)
    print("MIGRACIÓN A BASE DE DATOS POSTGRESQL")
    print("=" * 60)

    conn = connect_db()
    df = load_csv()

    try:
        insert_estudiantes(conn, df)
        insert_semestres(conn, df)
        insert_bimestres(conn, df)
        insert_asignaturas(conn, df)
        insert_paes(conn, df)
        insert_pdt(conn, df)
        insert_rendimiento_ramo(conn, df)

        print("\n" + "=" * 60)
        print("✓ MIGRACIÓN EXITOSA")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error durante el proceso: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
