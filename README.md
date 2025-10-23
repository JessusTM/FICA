# Proyecto FICA

El flujo de trabajo desarrollado permite:
- Eliminar ramos de la línea de **Álgebra** (Introducción al Álgebra, Álgebra, Matemáticas para la Computación I y II).
- Agrupar filas según el tipo de prueba (**PAES / PDT**).
- Asignar identificadores únicos a los estudiantes a partir de coincidencias en las columnas de sus resultados.
- Guardar los datos obtenidos en una base de datos PostgreSQL local.

## Requisitos previos

El proyecto requiere **Python 3.12 o superior y PostgreSQL 16.10 o superior**.  

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

#### Crear base de datos en PostgreSQL (Linux)

```bash
sudo systemctl status postgresql              # Verificar que el servicio esté activo
sudo psql -U postgres -f database.sql         # Crear base de datos y tablas
```

> **Nota:** En caso de que se utilice un usuario distinto al administrador **postgres**, será necesario otorgarle los permisos correspondientes haciendo uso del script `grant_permissions.sql`. De no realizar esta última acción el script `populate_database.py` fallará al interactuar con la base de datos y las tablas no serán creadas. Para evitar esto reemplaza tu nombre del usuario dentro del archivo `grant_permissions.sql` y luego ejecuta el siguiente comando en la terminal:

```bash 
sudo psql -U postgres -f grant_permissions.sql   # Otorga permisos al usuario
```

## Estructura del proyecto

```bash
FICA/
├── data/                                 # Carpeta para colocar el CSV original
├── database.sql                          # Crear tablas y constrains para la base de datos
├── grant_permissions.sql                 # Permisos de usuario para la base de datos 
├── README.md
├── requirements.txt                      # Dependencias del proyecto
└── scripts/
    ├── delete_algebra_classes.py         # Filtrar ramos
    ├── group_by_test.py                  # Agrupar filas por tipo de prueba (PAES / PDT)
    └── group_by_student.py               # Agrupa por estudiante (asigna IDs)
    └── populate_database.py              # Guardar datos en PostgreSQL
    └── db_config.py                      # Configuración de conexión la base de datos
```

## Flujo de ejecución de scripts

Antes de ejecutar el proceso ETL coloca una copia del archivo original con el nombre`fica-bimestres.csv` dentro de la carpeta `data/`.

Después, ejecuta el archivo`main.py` de la siguiente manera:
```bash
python3 main.py
```
Este script ejecutará de manera secuencial cada uno de los scripts ubicados en el directorio `scripts/`. Durante la ejecución se generan y consumen los siguientes archivos:

1. **`delete_algebra_classes.py`**
   - **Entrada:** `data/fica-bimestres.csv`
   - **Salida:** `data/1.fica-bimestres-calculus.csv`
   - **Función:** Elimina los ramos de la línea de Álgebra (Introducción al Álgebra, Álgebra, Matemática para la Computación I y II).

2. **`group_by_test.py`**
   - **Entrada:** `data/1.fica-bimestres-calculus.csv`
   - **Salida:** `data/2.fica_bimestres_grouped_by_test.csv`
   - **Función:** Agrupa las filas según el tipo de prueba rendida por el estudiante (**PAES / PDT**).

3. **`group_by_student.py`**
   - **Entrada:** `data/2.fica_bimestres_grouped_by_test.csv`
   - **Salida:** `data/3.fica_bimestres_grouped_by_student.csv`
   - **Función:** Asigna identificadores únicos a los estudiantes mediante coincidencias entre columnas de resultados, permitiendo vincular registros de un mismo estudiante.

4. **`populate_database.py`**
   - **Entrada:** `data/3.fica_bimestres_grouped_by_student.csv`
   - **Función:** Guarda los datos ya procesados en la base de datos de acorde a lo definido en el archivo `database.sql`.

## Modelo relacional base de datos
![alt text](https://github.com/JessusTM/FICA/blob/main/modelo_relacional.png?raw=true)
