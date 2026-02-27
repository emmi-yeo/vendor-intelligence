import os
import time
import pandas as pd
import pymssql
from typing import Dict
from dotenv import load_dotenv

load_dotenv()


# ============================
# 🔐 CONNECTION
# ============================

def get_connection():
    return pymssql.connect(
        server=os.getenv("AZURE_SQL_SERVER"),
        user=os.getenv("AZURE_SQL_USERNAME"),
        password=os.getenv("AZURE_SQL_PASSWORD"),
        database=os.getenv("AZURE_SQL_DATABASE"),
        port=1433,
        login_timeout=5,
        timeout=15  # execution timeout (seconds)
    )


# ============================
# 🚀 MAIN EXECUTOR
# ============================

def execute_sql_query(
    sql: str,
    max_rows: int = 100
) -> Dict:
    """
    Execute validated SQL safely.
    Returns structured execution result.
    """

    start_time = time.time()

    try:
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)

        cursor.execute(sql)

        rows = cursor.fetchall()

        conn.close()

        execution_time = round(time.time() - start_time, 3)

        # Enforce secondary row cap (extra safety)
        if len(rows) > max_rows:
            rows = rows[:max_rows]

        df = pd.DataFrame(rows)

        return {
            "success": True,
            "row_count": len(df),
            "execution_time_sec": execution_time,
            "dataframe": df
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "row_count": 0,
            "execution_time_sec": round(time.time() - start_time, 3),
            "dataframe": None
        }