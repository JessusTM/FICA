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
    "año_ingreso","tipo_ingreso",
]

def columnLetterToIndex(letter: str) -> int:
    text    = letter.strip().upper()
    value   = 0
    for char in text : value = value * 26 + (ord(char) - 64)
    return value - 1

def parseColumnRange(rangeText: str) -> tuple[int, int]:
    parts       = rangeText.split(":")
    startLetter = parts[0].strip()
    endLetter   = parts[1].strip()
    startIndex  = columnLetterToIndex(startLetter)
    endIndex    = columnLetterToIndex(endLetter)
    if startIndex > endIndex:
        startIndex, endIndex = endIndex, startIndex
    return startIndex, endIndex

def getDataRows(dataframe: pd.DataFrame, dataStartRow: int) -> pd.DataFrame:
    startIndex = dataStartRow - 1
    if startIndex < 0 : startIndex = 0
    return dataframe.iloc[startIndex:, :].copy()

def normalizeCell(cellValue):
    isMissing = pd.isna(cellValue)
    if isMissing : return None

    textValue        = str(cellValue)
    trimmedValue     = textValue.strip()
    isEmptyAfterTrim = trimmedValue == ""
    if isEmptyAfterTrim : return None
    return trimmedValue

def buildStudentKey(
    row: pd.Series,
    paesStart: int,
    paesEnd: int,
    pdtStart: int,
    pdtEnd: int) -> tuple | None:
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


def assignStudentIds(
    dataRows: pd.DataFrame,
    paesRange: str,
    pdtRange: str) -> pd.DataFrame:
    data                = dataRows.copy()
    paesStart, paesEnd  = parseColumnRange(paesRange)
    pdtStart, pdtEnd    = parseColumnRange(pdtRange)

    keyToId         = {}
    nextId          = 1
    studentIds      = []
    noneFlags       = []
    originalIndex   = []
    currentIndex    = 0

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
        originalIndex.append(currentIndex)
        currentIndex += 1

    data["studentId"]     = studentIds
    data["noScores"]      = noneFlags
    data["originalIndex"] = originalIndex
    return data

def orderByStudentId(dataWithIds: pd.DataFrame) -> pd.DataFrame:
    data        = dataWithIds.copy()
    numericKey  = []

    for value in data["studentId"]:
        if value == "":
            numericKey.append(-1)
        else:
            numericKey.append(int(value))

    data["studentIdOrder"]  = numericKey
    dataSorted              = data.sort_values(["noScores", "studentIdOrder", "originalIndex"])

    if "studentIdOrder" in dataSorted.columns:
        dataSorted = dataSorted.drop(columns=["studentIdOrder"])
    return dataSorted

def prependStudentIdColumn(
    dataSorted: pd.DataFrame,                       
    originalColumnCount: int,
    paesRange: str,
    pdtRange: str) -> pd.DataFrame:
    data = dataSorted.copy()

    # Eliminar columnas temporales del procesamiento
    if "noScores" in data.columns:
        data = data.drop(columns=["noScores"])
    if "originalIndex" in data.columns:
        data = data.drop(columns=["originalIndex"])
    if "group" in data.columns:
        data = data.drop(columns=["group"])

    if "studentId" not in data.columns:
        data.insert(0, "studentId", dataSorted["studentId"])
    else:
        columnOrder = ["studentId"]
        for col in data.columns:
            if col != "studentId":
                columnOrder.append(col)
        data = data[columnOrder]

    # Determinar tipo_ingreso basándose en los datos de PAES/PDT
    paesStart, paesEnd = parseColumnRange(paesRange)
    pdtStart, pdtEnd = parseColumnRange(pdtRange)

    tipo_ingreso_list = []
    for _, row in data.iterrows():
        # Verificar si hay datos en columnas PAES
        paes_data = row.iloc[paesStart:paesEnd+1]
        has_paes = False
        if paes_data.notna().any():
            has_paes = (paes_data.astype(str).str.strip() != "").any()

        # Verificar si hay datos en columnas PDT
        pdt_data = row.iloc[pdtStart:pdtEnd+1]
        has_pdt = False
        if pdt_data.notna().any():
            has_pdt = (pdt_data.astype(str).str.strip() != "").any()

        if has_paes:
            tipo_ingreso_list.append("PAES")
        elif has_pdt:
            tipo_ingreso_list.append("PDT")
        else:
            tipo_ingreso_list.append("")

    data["tipo_ingreso"] = tipo_ingreso_list

    return data

def computeSimpleCounts(dataWithIds: pd.DataFrame) -> tuple[int, int, int, int]:
    total = len(dataWithIds)

    withoutScores = 0
    if "noScores" in dataWithIds.columns:
        count = 0
        for value in dataWithIds["noScores"]:
            if bool(value):
                count += 1
        withoutScores = int(count)

    withScores = total - withoutScores

    uniqueIds = set()
    for value in dataWithIds["studentId"]:
        if value != "":
            uniqueIds.add(int(value))
    numStudents = len(uniqueIds)
    return total, withScores, withoutScores, numStudents

def group_by_student(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    dataframe               = df.copy()
    dataRows                = getDataRows(dataframe, DATA_START_ROW)
    dataWithIds             = assignStudentIds(dataRows, PAES_RANGE, PDT_RANGE)
    dataOrdered             = orderByStudentId(dataWithIds)
    originalColumnCount     = dataframe.shape[1]
    dataForOutput           = prependStudentIdColumn(dataOrdered, originalColumnCount, PAES_RANGE, PDT_RANGE)
    dataForOutput.columns   = HEADERS

    total, withScores, withoutScores, numStudents = computeSimpleCounts(dataWithIds)
    summary = {
        "total_rows"     : total,
        "with_scores"    : withScores,
        "without_scores" : withoutScores,
        "num_students"   : numStudents,
    }
    return dataForOutput, summary
