# Proyecto FICA

El flujo de trabajo desarrollado permite:
- Eliminar ramos de la línea de **Álgebra** (Introducción al Álgebra, Álgebra, Matemáticas para la Computación I y II).
- Agrupar filas según el tipo de prueba (**PAES / PDT**).
- Asignar identificadores únicos a los estudiantes a partir de coincidencias en las columnas de sus resultados.

## Requisitos previos

El proyecto requiere **Python 3.12 o superior**.  

#### Clonar el repositorio

```bash
git clone git@github.com:JessusTM/FICA.git
cd FICA
```

#### Crear entorno virtual

```bash
python3 -m venv .venv
```

#### Activar el entorno virtual

```bash
source .venv/bin/activate      # Linux / Mac
.venv\Scripts\activate         # Windows PowerShell
```

#### Instalar dependencias

```bash
pip install -r requirements.txt
```

## Estructura del proyecto

```bash
FICA/
├── data/
│   ├── fica-bimestres.csv                # CSV original sin limpiar
│   ├── 1.fica-bimestres-calculus.csv     
│   ├── 2.fica-bimestres_grouped_by_test.csv
│   └── 3.fica-bimestres_grouped_by_student.csv
├── database.sql                          # Base de Datos 
├── README.md
├── requirements.txt                      # Dependencias del proyecto
└── scripts/
    ├── delete_algebra_classes.py         # Filtrar ramos
    ├── group_by_test.py                  # Agrupar filas por tipo de prueba (PAES / PDT)
    └── group_by_student.py               # Agrupa por estudiante (asigna IDs)
```

## Flujo de ejecución de scripts

Cada script del proyecto debe ejecutarse de manera secuencial, ya que cada uno genera el archivo de entrada necesario para el siguiente paso.  
El orden correcto es el siguiente:

1. **`delete_algebra_classes.py`**  
   - **Entrada:** `data/fica-bimestres.csv`  
   - **Salida:** `data/1.fica-bimestres-calculus.csv`  
   - **Función:** Elimina los ramos de la línea de Álgebra (Introducción al Álgebra, Álgebra, Matemática para la Computación I y II).

2. **`group_by_test.py`**  
   - **Entrada:** `data/1.fica-bimestres-calculus.csv`  
   - **Salida:** `data/2.fica-bimestres_grouped_by_test.csv`  
   - **Función:** Agrupa las filas según el tipo de prueba rendida por el estudiante (**PAES / PDT**).

3. **`group_by_student.py`**  
   - **Entrada:** `data/2.fica-bimestres_grouped_by_test.csv`  
   - **Salida:** `data/3.fica-bimestres_grouped_by_student.csv`  
   - **Función:** Asigna identificadores únicos a los estudiantes mediante coincidencias entre columnas de resultados, permitiendo vincular registros de un mismo estudiante.

> **Nota:** Todos los scripts deben ejecutarse dentro de la carpeta `scripts/`, ya que utilizan rutas relativas hacia la carpeta `data/`.

## Flujo de ejecución de scripts

Cada script del proyecto debe ejecutarse de manera secuencial, ya que cada uno genera el archivo de entrada necesario para el siguiente paso. El orden correcto es el siguiente:

1. **`delete_algebra_classes.py`**  
   - **Entrada  :** `data/fica-bimestres.csv`  
   - **Salida   :** `data/1.fica-bimestres-calculus.csv`  
   - **Función  :** Elimina los ramos de la línea de Álgebra (Introducción al Álgebra, Álgebra, Matemática para la Computación I y II).

2. **`group_by_test.py`**  
   - **Entrada  :** `data/1.fica-bimestres-calculus.csv`  
   - **Salida   :** `data/2.fica-bimestres_grouped_by_test.csv`  
   - **Función  :** Agrupa las filas según el tipo de prueba rendida por el estudiante (**PAES / PDT**).

3. **`group_by_student.py`**  
   - **Entrada  :** `data/2.fica-bimestres_grouped_by_test.csv`  
   - **Salida   :** `data/3.fica-bimestres_grouped_by_student.csv`  
   - **Función  :** Asigna identificadores únicos a los estudiantes mediante coincidencias entre columnas de resultados, permitiendo vincular registros de un mismo estudiante.

> **Nota:** Todos los scripts deben ejecutarse dentro de la carpeta `scripts/`, ya que utilizan rutas relativas hacia la carpeta `data/`.

## Base de datos

El archivo `database.sql` contiene las instrucciones para crear la base de datos y las tablas necesarias. Para ejecutarlo se utiliza el siguiente comando en la terminal:

```bash 
sudo psql -U postgres -f database.sql
```
