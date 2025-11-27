from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
SCRIPTS_DIR = ROOT_DIR / "scripts"


class Step:
    def __init__(self, description: str, script: str, args: list[str] | None = None) -> None:
        self.description = description
        self.script = script
        self.args = args or []

    def command(self) -> list[str]:
        return [sys.executable, self.script, *self.args]


STEPS = [
    Step(
        "Eliminar ramos de Álgebra",
        "delete_algebra_classes.py",
        ["-i", "../data/fica-bimestres.csv"],
    ),
    Step(
        "Agrupar filas por tipo de prueba",
        "group_by_test.py",
        ["-i", "../data/1.fica-bimestres-calculus.csv"],
    ),
    Step(
        "Agrupar filas por estudiante",
        "group_by_student.py",
        ["-i", "../data/2.fica_bimestres_grouped_by_test.csv"],
    ),
    Step(
        "Cargar datos procesados en PostgreSQL",
        "populate_database.py",
    ),
]


def ensure_input_exists() -> None:
    expected = DATA_DIR / "fica-bimestres.csv"
    if not expected.exists():
        message = (
            "No se encontró el archivo de entrada 'data/fica-bimestres.csv'.\n"
            "Copia el CSV original dentro de la carpeta 'data/' y vuelve a ejecutar el script."
        )
        print(message)
        sys.exit(1)


def run_step(step: Step) -> None:
    script_path = SCRIPTS_DIR / step.script
    if not script_path.exists():
        raise FileNotFoundError(f"No se encontró el script: {script_path}")

    print(f"\n→ {step.description}")
    try:
        subprocess.run(step.command(), cwd=SCRIPTS_DIR, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"✗ Error al ejecutar {step.script}: {exc}")
        sys.exit(exc.returncode or 1)


def main() -> None:
    ensure_input_exists()

    for step in STEPS:
        run_step(step)

    print("\n✓ Flujo de procesamiento finalizado correctamente.")


if __name__ == "__main__":
    main()
