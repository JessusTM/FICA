from typing import Any, Dict, Tuple, Optional

import pandas as pd
from sqlalchemy.engine import Engine

from app.services.etl.delete_algebra_classes import filter_out_algebra
from app.services.etl.group_by_test import group_by_test
from app.services.etl.group_by_student import group_by_student
from app.services.etl.populate_database import populate_all
from app.core.database.db import engine as default_engine, get_raw_connection

def run_pipeline_on_dataframe(
    df          : pd.DataFrame,
    db_engine   : Optional[Engine] = None,
) -> Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]]:
    df0                         = df.copy()
    df1, summary_filter         = filter_out_algebra(df0)
    df2, summary_group_test     = group_by_test(df1)
    df3, summary_group_student  = group_by_student(df2)

    if db_engine is None:
        with get_raw_connection() as conn:
            summary_db = populate_all(conn, df3)
    else:
        conn = db_engine.raw_connection()
        try:
            summary_db = populate_all(conn, df3)
        finally:
            conn.close()

    summary: Dict[str, Dict[str, Any]] = {
        "filter_out_algebra"   : summary_filter,
        "group_by_test"        : summary_group_test,
        "group_by_student"     : summary_group_student,
        "database"             : summary_db,
    }
    return df3, summary
