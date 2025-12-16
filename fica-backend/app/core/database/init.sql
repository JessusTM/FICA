CREATE TABLE estudiantes (
  id_estudiante   BIGINT PRIMARY KEY,
  anio_ingreso    INT NOT NULL,
  tipo_prueba     TEXT NOT NULL CHECK (tipo_prueba IN ('PAES', 'PDT')),
  nem             NUMERIC(6,2),
  ranking         NUMERIC(6,2),
  prueba_diagnostico_matematica NUMERIC(5,2)
);

CREATE TABLE semestres (
  id_semestre     BIGSERIAL PRIMARY KEY,
  anio            INT NOT NULL CHECK (anio BETWEEN 2000 AND 2100),
  numero          INT NOT NULL CHECK (numero IN (1,2)),
  UNIQUE (anio, numero)
);

CREATE TABLE bimestres (
  id_bimestre     BIGSERIAL PRIMARY KEY,
  id_semestre     BIGINT NOT NULL,
  numero          INT NOT NULL CHECK (numero IN (1,2,3,4)),
  UNIQUE (id_semestre, numero),
  FOREIGN KEY (id_semestre) REFERENCES semestres(id_semestre) ON DELETE CASCADE
);

CREATE TABLE asignaturas (
  id_asignatura   BIGSERIAL PRIMARY KEY,
  codigo          TEXT NOT NULL,
  modulo          TEXT,
  nombre          TEXT NOT NULL,
  UNIQUE (codigo, modulo, nombre)
);

CREATE TABLE lineas (
  id_linea        BIGSERIAL PRIMARY KEY,
  nombre          TEXT NOT NULL UNIQUE,
  descripcion     TEXT
);

CREATE TABLE linea_asignaturas (
  id_linea        BIGINT NOT NULL,
  id_asignatura   BIGINT NOT NULL,
  PRIMARY KEY (id_linea, id_asignatura),
  FOREIGN KEY (id_linea) REFERENCES lineas(id_linea) ON DELETE CASCADE,
  FOREIGN KEY (id_asignatura) REFERENCES asignaturas(id_asignatura) ON DELETE CASCADE
);

CREATE TABLE rendimiento_ramo (
  id_rendimiento  BIGSERIAL PRIMARY KEY,
  id_estudiante   BIGINT NOT NULL,
  id_bimestre     BIGINT NOT NULL,
  id_asignatura   BIGINT NOT NULL,
  nota_final      NUMERIC(4,2),
  estado_final    TEXT,
  fecha_creacion  TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (id_estudiante, id_bimestre, id_asignatura),
  FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE,
  FOREIGN KEY (id_bimestre) REFERENCES bimestres(id_bimestre) ON DELETE CASCADE,
  FOREIGN KEY (id_asignatura) REFERENCES asignaturas(id_asignatura) ON DELETE RESTRICT
);

CREATE TABLE paes (
  id_paes           BIGSERIAL PRIMARY KEY,
  id_estudiante     BIGINT NOT NULL,
  anio_examen       INT,
  c_lectora         NUMERIC(6,2),
  m1                NUMERIC(6,2),
  m2                NUMERIC(6,2),
  historia          NUMERIC(6,2),
  ciencias          NUMERIC(6,2),
  prom_m1_clectora  NUMERIC(6,2),
  fecha_creacion    TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (id_estudiante, anio_examen),
  FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE
);

CREATE TABLE pdt (
  id_pdt            BIGSERIAL PRIMARY KEY,
  id_estudiante     BIGINT NOT NULL,
  anio_examen       INT,
  lenguaje          NUMERIC(6,2),
  matematicas       NUMERIC(6,2),
  historia          NUMERIC(6,2),
  ciencias          NUMERIC(6,2),
  prom_leng_mat     NUMERIC(6,2),
  fecha_creacion    TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (id_estudiante, anio_examen),
  FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE
);

CREATE TABLE perfil_ingreso_academico_estudiante (
  id_estudiante           BIGINT PRIMARY KEY,
  tipo_prueba             TEXT NOT NULL CHECK (tipo_prueba IN ('PAES', 'PDT')),
  anio_examen_relevante   INT,
  indice_perfil_academico NUMERIC(8,4),
  fecha_creacion          TIMESTAMPTZ NOT NULL DEFAULT now(),
  FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE
);

CREATE TABLE carga_csv (
  id_carga          BIGSERIAL PRIMARY KEY,
  nombre_archivo    TEXT NOT NULL,
  fecha_carga       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE gold_kpi_b1_student (
  cohorte         int     NOT NULL,
  id_estudiante   BIGINT  NOT NULL,
  tipo_prueba     text    NULL,
  puntaje_ingreso double precision NULL,
  diagnostico     double precision NULL,
  nota_b1         double precision NULL,
  PRIMARY KEY (cohorte, id_estudiante)
);

CREATE INDEX idx_gold_kpi_b1_student_cohorte
  ON gold_kpi_b1_student (cohorte);

CREATE INDEX idx_gold_kpi_b1_student_cohorte_nota
  ON gold_kpi_b1_student (cohorte, nota_b1);

CREATE TABLE gold_kpi_student_ramos (
  cohorte       int     NOT NULL,
  id_estudiante BIGINT  NOT NULL,
  total_ramos   int     NOT NULL,
  PRIMARY KEY (cohorte, id_estudiante)
);

CREATE INDEX idx_gold_kpi_student_ramos_cohorte
  ON gold_kpi_student_ramos (cohorte);

CREATE INDEX idx_gold_kpi_student_ramos_cohorte_total
  ON gold_kpi_student_ramos (cohorte, total_ramos);

CREATE TABLE gold_kpi_student_aprueba8 (
  cohorte       int     NOT NULL,
  id_estudiante BIGINT  NOT NULL,
  aprueba_8     int     NOT NULL,
  PRIMARY KEY (cohorte, id_estudiante)
);

CREATE INDEX idx_gold_kpi_student_aprueba8_cohorte
  ON gold_kpi_student_aprueba8 (cohorte);

CREATE INDEX idx_gold_kpi_student_aprueba8_cohorte_flag
  ON gold_kpi_student_aprueba8 (cohorte, aprueba_8);
