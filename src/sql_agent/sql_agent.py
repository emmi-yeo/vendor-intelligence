from typing import Dict
from src.sql_agent.schema_loader import (
    load_schema_cache,
    get_schema_summary_for_llm
)
from src.sql_agent.planner import generate_query_plan
from src.sql_agent.sql_generator import generate_sql_from_plan
from src.sql_agent.validator import validate_sql
from src.sql_agent.executor import execute_sql_query


# ============================
# 🚀 MAIN ORCHESTRATOR
# ============================

def run_sql_agent(
    user_query: str,
    has_uploaded_file: bool = False
) -> Dict:
    """
    Full SQL Agent pipeline:
    Plan → Generate SQL → Validate → Execute
    """

    try:
        # --------------------------------
        # 1️⃣ Load schema
        # --------------------------------
        schema = load_schema_cache()
        schema_summary = get_schema_summary_for_llm(schema)

        # --------------------------------
        # 2️⃣ Generate structured plan
        # --------------------------------
        plan = generate_query_plan(
            user_query=user_query,
            schema_summary=schema_summary,
            has_uploaded_file=has_uploaded_file
        )

        # If planner says RAG required only, skip SQL
        if plan.get("requires_rag") and not plan.get("tables"):
            return {
                "success": True,
                "mode": "rag_only",
                "plan": plan,
                "sql": None,
                "validation": None,
                "execution": None,
                "dataframe": None
            }

        # --------------------------------
        # 3️⃣ Generate SQL
        # --------------------------------
        sql_output = generate_sql_from_plan(plan, schema)
        sql_query = sql_output["sql"]

        # --------------------------------
        # 4️⃣ Validate SQL
        # --------------------------------
        validation = validate_sql(
            sql=sql_query,
            allowed_tables=plan.get("tables", [])
        )

        if not validation["valid"]:
            return {
                "success": False,
                "stage": "validation_failed",
                "reason": validation["reason"],
                "plan": plan,
                "sql": sql_query
            }

        # --------------------------------
        # 5️⃣ Execute SQL
        # --------------------------------
        execution = execute_sql_query(sql_query)

        if not execution["success"]:
            return {
                "success": False,
                "stage": "execution_failed",
                "error": execution["error"],
                "plan": plan,
                "sql": sql_query
            }

        # --------------------------------
        # 6️⃣ Return structured result
        # --------------------------------
        return {
            "success": True,
            "mode": "sql",
            "plan": plan,
            "sql": sql_query,
            "validation": validation,
            "execution_time_sec": execution["execution_time_sec"],
            "row_count": execution["row_count"],
            "dataframe": execution["dataframe"]
        }

    except Exception as e:
        return {
            "success": False,
            "stage": "unexpected_error",
            "error": str(e)
        }