from typing import Any, Dict, Tuple, Optional
import numpy as np
import pandas as pd
from sqlalchemy.engine import Engine

from app.services.etl.delete_algebra_classes import filter_out_algebra
from app.services.etl.group_by_test import group_by_test
from app.services.etl.group_by_student import group_by_student
from app.services.etl.populate_database import populate_all
from app.core.database.db import engine as default_engine, get_raw_connection
from app.services.etl_state import etl_state_manager


def convert_numpy_types(obj):
    """
    Recursively convert numpy types to native Python types for JSON serialization.
    """
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    else:
        return obj

def run_pipeline_on_dataframe(
    df          : pd.DataFrame,
    db_engine   : Optional[Engine] = None,
) -> Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]]:
    try:
        etl_state_manager.start_process()

        df0 = df.copy()

        # Step 1: Filter out algebra classes
        etl_state_manager.update_step(1)
        df1, summary_filter = filter_out_algebra(df0)

        # Step 2: Group by test
        etl_state_manager.update_step(2)
        df2, summary_group_test = group_by_test(df1)

        # Step 3: Group by student
        etl_state_manager.update_step(3)
        df3, summary_group_student = group_by_student(df2)

        # Step 4: Populate database
        etl_state_manager.update_step(4)
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

        # Convert numpy types to native Python types for JSON serialization
        summary = convert_numpy_types(summary)

        etl_state_manager.complete_process()
        return df3, summary
    except Exception as e:
        etl_state_manager.fail_process(str(e))
        raise
