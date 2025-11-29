import argparse
from pathlib import Path
import sys
import pandas as pd

DATA_START_ROW  = 1
PAES_RANGE      = "J:Q"
PDT_RANGE       = "R:X"
HEADERS         = [
    "id_alumno","año","semestre","bimestre","codigo_asignatura","modulo",
    "nombre_asignatura","nota_final","estado_final","diagnostico_matematica",
    "paes_comprension_lectora","paes_m1","paes_m2","paes_historia","paes_ciencias",
    "paes_nem","paes_ranking","paes_promedio_m1_comprension_lectora",
    "pdt_lenguaje","pdt_matematicas","pdt_historia","pdt_ciencias",
    "pdt_nem","pdt_ranking","pdt_promedio_matematicas_lenguaje",
    "año_ingreso","tipo_ingreso","id_registro"
]

def columnLetterToIndex(letter):
    text    = letter.strip().upper()
    value   = 0
    for char in text:
        value = value * 26 + (ord(char) - 64)
    return value - 1


def parseColumnRange(rangeText):
    parts       = rangeText.split(":")
    startLetter = parts[0].strip()
    endLetter   = parts[1].strip()
    startIndex  = columnLetterToIndex(startLetter)
    endIndex    = columnLetterToIndex(endLetter)
    if startIndex > endIndex:
        temp        = startIndex
        startIndex  = endIndex
        endIndex    = temp
    return startIndex, endIndex


def parseCliArgs():
    parser      = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-i", "--input", required=True)
    args        = parser.parse_args()
    inputPath   = Path(args.input)

    if not inputPath.exists() : sys.exit(1)
    
    return inputPath


def getDataRows(dataframe, dataStartRow):
    startIndex = dataStartRow - 1
    if startIndex < 0:
        startIndex = 0
    return dataframe.iloc[startIndex:, :].copy()


def normalizeCell(cellValue):
    isMissing = pd.isna(cellValue)
    if isMissing : return None

    textValue           = str(cellValue)
    trimmedValue        = textValue.strip()
    isEmptyAfterTrim    = trimmedValue == ""
    if isEmptyAfterTrim : return None

    return trimmedValue


def buildStudentKey(row, paesStart, paesEnd, pdtStart, pdtEnd):
    values      = []
    colIndex    = paesStart
    while colIndex <= paesEnd:
        values.append(normalizeCell(row[colIndex]))
        colIndex += 1
    colIndex    = pdtStart
    while colIndex <= pdtEnd:
        values.append(normalizeCell(row[colIndex]))
        colIndex += 1

    allEmpty = True
    for v in values:
        if v is not None:
            allEmpty = False
            break
    if allEmpty : return None

    return tuple(values)


def assignStudentIds(dataRows, paesRange, pdtRange):
    data                = dataRows.copy()
    paesStart, paesEnd  = parseColumnRange(paesRange)
    pdtStart, pdtEnd    = parseColumnRange(pdtRange)

    keyToId         = {}
    nextId          = 1
    studentIds      = []
    noneFlags       = []
    originalIndex   = []
    idx             = 0
    
    for _, row in data.iterrows():
        key = buildStudentKey(row, paesStart, paesEnd, pdtStart, pdtEnd)
        if key is None:
            studentIds.append("")
            noneFlags.append(True)
        else:
            if key in keyToId:
                studentIds.append(keyToId[key])
            else:
                keyToId[key] = nextId
                studentIds.append(nextId)
                nextId += 1
            noneFlags.append(False)
        originalIndex.append(idx)
        idx += 1

    data["studentId"]       = studentIds
    data["noScores"]        = noneFlags
    data["originalIndex"]   = originalIndex

    return data


def orderByStudentId(dataWithIds):
    data = dataWithIds.copy()

    numericKey = []
    for v in data["studentId"]:
        if v == "":
            numericKey.append(-1)
        else:
            numericKey.append(int(v))
    data["studentIdOrder"] = numericKey

    dataSorted = data.sort_values(["noScores", "studentIdOrder", "originalIndex"])

    if "studentIdOrder" in dataSorted.columns:
        dataSorted = dataSorted.drop(columns=["studentIdOrder"])

    return dataSorted


def prependStudentIdColumn(dataSorted, originalColumnCount):
    data = dataSorted.copy()

    if "noScores" in data.columns:
        data = data.drop(columns=["noScores"])
    if "originalIndex" in data.columns:
        data = data.drop(columns=["originalIndex"])

    if "studentId" not in data.columns:
        data.insert(0, "studentId", dataSorted["studentId"])
        return data

    columnOrder = []
    columnOrder.append("studentId")
    for col in data.columns:
        if col != "studentId":
            columnOrder.append(col)

    data = data[columnOrder]
    return data


def computeSimpleCounts(dataWithIds):
    total = len(dataWithIds)

    withoutScores = 0
    if "noScores" in dataWithIds.columns:
        count = 0
        for v in dataWithIds["noScores"]:
            if bool(v):
                count += 1
        withoutScores = int(count)

    withScores = total - withoutScores

    uniqueIds = set()
    for v in dataWithIds["studentId"]:
        if v != "":
            uniqueIds.add(int(v))
    numStudents = len(uniqueIds)

    return total, withScores, withoutScores, numStudents


def printSummary(inputPath, outputPath, counts):
    total, withScores, withoutScores, numStudents = counts
    print("----- RESULTADO DE LA AGRUPACIÓN POR ESTUDIANTE -----")
    print(f"    Entrada          : {inputPath.name}")
    print(f"    Salida           : {outputPath.name}")
    print(f"    Filas totales    : {total}")
    print(f"    Estudiantes      : {numStudents}")


def processFile(inputPath):
    dataframe               = pd.read_csv(inputPath, header=None)
    dataRows                = getDataRows(dataframe, DATA_START_ROW)
    dataWithIds             = assignStudentIds(dataRows, PAES_RANGE, PDT_RANGE)
    dataOrdered             = orderByStudentId(dataWithIds)
    originalColumnCount     = dataframe.shape[1]
    dataForOutput           = prependStudentIdColumn(dataOrdered, originalColumnCount)
    dataForOutput.columns   = HEADERS
    outputPath              = Path("../data/3.fica_bimestres_grouped_by_student.csv")
    dataForOutput.to_csv(outputPath, index=False, header=True)
    counts                  = computeSimpleCounts(dataWithIds)
    printSummary(inputPath, outputPath, counts)


def main():
    inputPath = parseCliArgs()
    processFile(inputPath)


if __name__ == "__main__":
    main()
