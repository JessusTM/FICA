import pandas as pd

ALGEBRA_CLASSES = [
    "INTRODUCCIÓN AL ÁLGEBRA",
    "ÁLGEBRA",
    "MATEMÁTICA PARA LA COMPUTACIÓN I",
    "MATEMÁTICA PARA LA COMPUTACIÓN II",
]

def filter_out_algebra(df: pd.DataFrame):
    col_name            = df.columns[5]
    total_rows          = len(df)
    calculus_classes    = []
    removed_count       = 0

    for row_index, row in df.iterrows():
        course_name_raw     = row[col_name]
        course_name         = str(course_name_raw).strip()
        is_algebra_course   = course_name in ALGEBRA_CLASSES

        if not is_algebra_course:
            calculus_classes.append(row)
        else:
            removed_count += 1

    df_filtered = pd.DataFrame(calculus_classes)
    summary     = {
        "total_rows"    : total_rows,
        "removed_rows"  : removed_count,
        "remaining_rows": len(df_filtered),
        "course_column" : col_name,
    }
    return df_filtered, summary
