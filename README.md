# 📊 Proyecto FICA — Limpieza y agrupamiento de datos académicos

El flujo de trabajo desarrollado permite:
- Eliminar ramos de la línea de **Álgebra** (Introducción al Álgebra, Álgebra, Matemáticas para la Computación I y II).
- Agrupar filas según el tipo de prueba (**PAES / PDT**).
- Asignar identificadores únicos a los estudiantes a partir de coincidencias en las columnas de sus resultados.

## ⚙️ Requisitos previos

El proyecto requiere **Python 3.12 o superior**.  

```bash
# Clonar el repositorio
git clone <URL-del-repositorio>
cd FICA

# Crear entorno virtual
python3 -m venv .venv

# Activar el entorno virtual
source .venv/bin/activate        # En Linux o Mac
# .venv\Scripts\activate         # En Windows PowerShell

# Instalar dependencias
pip install -r requirements.txt
```

## 📁 Estructura del proyecto

```bash
FICA/
├── data/
│   ├── fica-bimestres.csv                # CSV original sin limpiar
│   ├── 1.fica-bimestres-calculus.csv     
│   ├── 2.fica-bimestres_grouped_by_test.csv
│   └── 3.fica-bimestres_grouped_by_student.csv
├── scripts/
│   ├── delete_algebra_classes.py         # Filtra ramos no deseados
│   ├── group_by_test.py                  # Agrupa filas por tipo de prueba (PAES / PDT)
│   └── group_by_student.py               # Agrupa por estudiante (asigna IDs)
├── requirements.txt                      # Dependencias del proyecto
└── README.md
```

> 🧠 **Importante:**
> Los scripts deben ejecutarse **únicamente dentro de la carpeta `scripts/`**, ya que utilizan rutas relativas (`../data/...`) para acceder al archivo de entrada y generar los CSV resultantes dentro de la carpeta `data/`.
