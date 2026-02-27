import json
from typing import Dict
from src.utils.llm_client import call_llm_json


# ============================
# 🧠 SYSTEM PROMPT
# ============================

SYSTEM_PROMPT = """
You are a SQL generation engine.

Your task:
Given:
- A structured query plan
- Full schema metadata

Generate a SAFE SQL SELECT query.

Rules:
- SELECT only.
- Must include TOP 50 unless aggregation requested.
- No DELETE, UPDATE, INSERT, DROP, ALTER.
- No system tables.
- Use only tables present in the plan.
- Use only columns that exist in schema.
- Use proper JOINs based on foreign keys.
- No SELECT *.
- No subqueries unless absolutely required.

Return JSON:
{
  "sql": "",
  "tables_used": [],
  "notes": []
}
"""


# ============================
# 📦 MAIN FUNCTION
# ============================

def generate_sql_from_plan(plan: Dict, schema: Dict) -> Dict:

    # Extract only relevant tables from schema
    relevant_tables = [
        table for table in schema["tables"]
        if table["name"] in plan.get("tables", [])
    ]

    user_prompt = f"""
Structured Plan:
{json.dumps(plan, indent=2)}

Relevant Schema Metadata:
{json.dumps(relevant_tables, indent=2)}

Generate SQL now.
"""

    response = call_llm_json(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.1
    )

    return response