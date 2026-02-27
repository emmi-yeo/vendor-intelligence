import json
from typing import Dict
from src.utils.llm_client import call_llm_json


# ============================
# 🧠 SYSTEM PROMPT
# ============================

SYSTEM_PROMPT = """
You are a database query planning agent.

Your task:
Given:
- A user query
- A database schema summary
- Whether a document was uploaded

You must generate a structured execution plan.

Rules:
- DO NOT generate SQL.
- DO NOT hallucinate tables not present in schema.
- Only use tables that exist in schema summary.
- Be precise.
- If user mentions ranking or totals, define aggregation.
- If uploaded file is present and user refers to requirements,
  set requires_rag = true.
- If document-only vendor matching, set requires_rag = true.
- If structured DB query only, set requires_rag = false.

Output must be valid JSON.
"""


# ============================
# 📦 MAIN PLANNER FUNCTION
# ============================

def generate_query_plan(
    user_query: str,
    schema_summary: str,
    has_uploaded_file: bool = False
) -> Dict:

    user_prompt = f"""
User Query:
{user_query}

Schema Summary:
{schema_summary}

Document Uploaded:
{has_uploaded_file}

Return JSON with structure:
{{
  "intent": "",
  "tables": [],
  "columns": [],
  "filters": {{}},
  "aggregations": {{
      "type": "",
      "column": ""
  }},
  "requires_rag": false,
  "reasoning": []
}}
"""

    response = call_llm_json(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.2
    )

    return response