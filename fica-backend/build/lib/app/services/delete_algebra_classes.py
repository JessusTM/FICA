import argparse
import pandas as pd
from pathlib import Path
import sys


ALGEBRA_CLASSES = [
    "INTRODUCCIÓN AL ÁLGEBRA",
    "ÁLGEBRA",
    "MATEMÁTICA PARA LA COMPUTACIÓN I",
    "MATEMÁTICA PARA LA COMPUTACIÓN II",
]


def parseCLIargs():
    parser      = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-i", "--input", required=True)
    args        = parser.parse_args()
    inputPath   = Path(args.input)
    if not inputPath.exists() : sys.exit(1)
    return inputPath


def deleteAlgebraClasses(inputPath):
    df          = pd.read_csv(inputPath, header=1)
    col_name    = df.columns[5]  
    total_rows  = len(df)

    calculus_classes    = []
    removed_count       = 0

    for _, row in df.iterrows():
        course = str(row[col_name]).strip()
        if course not in ALGEBRA_CLASSES:
            calculus_classes.append(row)
        else:
            removed_count += 1

    df_filtered = pd.DataFrame(calculus_classes)
    out_path    = Path("../data/1.fica-bimestres-calculus.csv")
    df_filtered.to_csv(out_path, index=False)

    return total_rows, removed_count, len(df_filtered), out_path

def printSummary(total, removed, remaining, out_path):
    print("\n------ RESULTADOS DEL FILTRADO ------")
    print(f"    Filas totales     : {total}")
    print(f"    Filas eliminadas  : {removed}")
    print(f"    Filas restantes   : {remaining}")
    print(f"    Archivo generado  : {out_path}")


def main():
    inputPath = parseCLIargs()
    total, removed, remaining, out_path = deleteAlgebraClasses(inputPath)
    printSummary(total, removed, remaining, out_path)

if __name__ == "__main__":
    main()
