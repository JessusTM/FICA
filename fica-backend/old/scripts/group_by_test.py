import argparse
from pathlib import Path
import sys
import pandas as pd
import numpy as np

DATA_START_ROW  = 3
PAES_RANGE      = "J:Q"
PDT_RANGE       = "R:X"
ORDER           = [
    "none", 
    "pdt", 
    "paes"
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
        startIndex, endIndex = endIndex, startIndex
    return startIndex, endIndex


def hasAnyData(row, startColumn, endColumn):
    cellRange       = row[startColumn : endColumn + 1]
    nonNullCells    = cellRange.dropna()

    if nonNullCells.empty : return False

    stringValues    = nonNullCells.astype(str)
    trimmedValues   = stringValues.str.strip()
    hasContent      = (trimmedValues != "").any()
    return hasContent


def classifyRow(row, paesColumns, pdtColumns):
    paesStart, paesEnd  = paesColumns
    pdtStart, pdtEnd    = pdtColumns
    hasPaesData         = hasAnyData(row, paesStart, paesEnd)
    hasPdtData          = hasAnyData(row, pdtStart, pdtEnd)

    if hasPdtData   : return "pdt"
    if hasPaesData  : return "paes"
    
    return "none"


def parseCliArgs():
    parser      = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-i", "--input", required=True)
    args        = parser.parse_args()
    inputPath   = Path(args.input)

    if not inputPath.exists() : sys.exit(1)

    return inputPath


def getDataRows(dataframe, dataStartRow):
    startIndex = max(dataStartRow - 1, 0)
    return dataframe.iloc[startIndex:, :].copy()


def classifyRows(dataRows, paesRange, pdtRange):
    data                = dataRows.copy()
    paesStart, paesEnd  = parseColumnRange(paesRange)
    pdtStart, pdtEnd    = parseColumnRange(pdtRange)
    groups              = []

    for _, row in data.iterrows():
        paes    = hasAnyData(row, paesStart, paesEnd)
        pdt     = hasAnyData(row, pdtStart, pdtEnd)
        if paes     : groups.append("paes")
        elif pdt    : groups.append("pdt")
        else        : groups.append("none")

    data["group"]           = groups
    data["originalIndex"]   = np.arange(len(data))
    return data


def orderRows(dataRowsWithGroup, order):
    groupOrderMap   = {}
    position        = 0
    for groupName in order:
        groupOrderMap[groupName] = position
        position += 1

    data            = dataRowsWithGroup.copy()
    defaultOrder    = len(order)
    sortOrderValues = []

    for _, row in data.iterrows():
        currentGroup    = row["group"] if "group" in row else None
        sortValue       = groupOrderMap.get(currentGroup, defaultOrder)
        sortOrderValues.append(sortValue)

    data["sortOrder"]   = sortOrderValues
    dataSorted          = data.sort_values(["sortOrder", "originalIndex"])
    dataSorted          = dataSorted.drop(columns=["sortOrder"])
    return dataSorted


def computeGroupCounts(dataWithGroup, order):
    counts = {}
    for name in order:
        counts[name] = 0

    if "group" in dataWithGroup:
        for _, row in dataWithGroup.iterrows():
            value = row["group"]
            if value in counts:
                counts[value] += 1
            else:
                pass
    return counts


def printSummary(inputPath, outputPath, totalRows, processedRows, groupCounts, order):
    print("\n----- RESULTADO DE LA AGRUPACIÓN POR PAES/PDT -----")
    print(f"    Entrada             : {inputPath.name}")
    print(f"    Salida              : {outputPath.name}")
    print(f"    Filas Totales       : {totalRows}")
    print(f"    Filas Procesadas    : {processedRows}")
    print(f"    Filas Ignoradas     : {totalRows - processedRows}")

    indent  = " " * 8
    lines   = [f"{name}: {groupCounts.get(name, 0)}" for name in order]
    width   = max(len(s) for s in lines) if lines else 0
    border  = indent + "+" + "-" * (width + 2) + "+"

    print(border)
    for s in lines:
        print(f"{indent}| {s.ljust(width)} |")
    print(border)


def processFile(inputPath):
    dataframe       = pd.read_csv(inputPath, header=None)
    dataRows        = getDataRows(dataframe, DATA_START_ROW)
    dataWithGroup   = classifyRows(dataRows, PAES_RANGE, PDT_RANGE)
    dataOrdered     = orderRows(dataWithGroup, ORDER)
    outputPath      = Path("../data/2.fica_bimestres_grouped_by_test.csv")
    dataOrdered.to_csv(outputPath, index=False, header=False)
    totalRows       = len(dataframe)
    processedRows   = len(dataRows)
    groupCounts     = computeGroupCounts(dataWithGroup, ORDER)
    printSummary(inputPath, outputPath, totalRows, processedRows, groupCounts, ORDER)


def main():
    inputPath = parseCliArgs()
    processFile(inputPath)


if __name__ == "__main__":
    main()
