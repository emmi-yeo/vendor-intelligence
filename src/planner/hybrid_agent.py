from typing import Dict
from src.planner.hybrid_planner import generate_hybrid_plan
from src.sql_agent.sql_agent import run_sql_agent
from src.rag.rag_pipeline import run_rag_pipeline
from src.planner.merge_and_score import score_vendors_against_requirements

def run_hybrid_agent(
    user_query: str,
    uploaded_file=None
) -> Dict:

    has_file = uploaded_file is not None

    hybrid_plan = generate_hybrid_plan(
        user_query=user_query,
        has_uploaded_file=has_file
    )

    mode = hybrid_plan.get("mode")

    sql_result = None
    rag_result = None

    if mode in ["sql_only", "sql_and_rag"]:
        sql_result = run_sql_agent(
            user_query=user_query,
            has_uploaded_file=has_file
        )

    if mode in ["rag_only", "sql_and_rag"] and uploaded_file:
        rag_result = run_rag_pipeline(
            uploaded_file=uploaded_file,
            user_query=user_query
        )

    scored_result = None

    if sql_result and rag_result:
        if sql_result.get("dataframe") is not None:
            scored_result = score_vendors_against_requirements(
                sql_result["dataframe"],
                rag_result
            )

    return {
        "hybrid_plan": hybrid_plan,
        "sql_result": sql_result,
        "rag_result": rag_result,
        "scored_result": scored_result
    }