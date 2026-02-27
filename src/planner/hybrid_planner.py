import json
from typing import Dict
from src.utils.llm_client import call_llm_json


SYSTEM_PROMPT = """
You are a Hybrid Planning Agent for a Vendor Intelligence System.

Your job:
Decide how to handle the user request.

Available engines:
1. SQL Agent (structured database queries)
2. RAG Pipeline (uploaded document requirement extraction)

Rules:

- If user asks for structured vendor filtering (industry, location, certification, spend),
  use SQL.

- If user uploads a requirement document, use RAG.

- If document requires matching vendors to requirements,
  use BOTH SQL and RAG.

- If only document summarization is needed,
  use RAG only.

- Always return structured JSON.

Output format:
{
  "mode": "sql_only | rag_only | sql_and_rag",
  "execution_steps": [],
  "reasoning": []
}
"""


def generate_hybrid_plan(
    user_query: str,
    has_uploaded_file: bool
) -> Dict:

    user_prompt = f"""
User Query:
{user_query}

Document Uploaded:
{has_uploaded_file}

Decide the best execution mode.
"""

    response = call_llm_json(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.2
    )

    return response