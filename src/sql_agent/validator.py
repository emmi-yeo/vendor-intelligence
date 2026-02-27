import re
import sqlparse
from typing import Dict, List


FORBIDDEN_KEYWORDS = [
    "DELETE",
    "UPDATE",
    "INSERT",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "EXEC",
    "MERGE",
    "GRANT",
    "REVOKE",
    "CREATE"
]


def extract_table_names(parsed) -> List[str]:
    """
    Extract table names from parsed SQL.
    Basic implementation: look for tokens after FROM and JOIN.
    """
    tables = []
    tokens = parsed.tokens

    for i, token in enumerate(tokens):
        if token.ttype is None:
            token_str = str(token).upper()

            if "FROM" in token_str or "JOIN" in token_str:
                parts = token_str.split()
                for j, part in enumerate(parts):
                    if part in ("FROM", "JOIN") and j + 1 < len(parts):
                        tables.append(parts[j + 1].replace(",", ""))

    return tables


def validate_sql(
    sql: str,
    allowed_tables: List[str],
    enforce_top: bool = True
) -> Dict:

    sql_upper = sql.upper().strip()

    # -----------------------------------
    # 1️⃣ Single statement only
    # -----------------------------------
    if ";" in sql_upper[:-1]:
        return {
            "valid": False,
            "reason": "Multiple SQL statements detected."
        }

    # -----------------------------------
    # 2️⃣ Must start with SELECT
    # -----------------------------------
    if not sql_upper.startswith("SELECT"):
        return {
            "valid": False,
            "reason": "Only SELECT statements are allowed."
        }

    # -----------------------------------
    # 3️⃣ Forbidden keywords
    # -----------------------------------
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", sql_upper):
            return {
                "valid": False,
                "reason": f"Forbidden keyword detected: {keyword}"
            }

    # -----------------------------------
    # 4️⃣ Parse SQL
    # -----------------------------------
    parsed = sqlparse.parse(sql)

    if not parsed:
        return {
            "valid": False,
            "reason": "SQL parsing failed."
        }

    statement = parsed[0]

    # -----------------------------------
    # 5️⃣ Enforce TOP clause
    # -----------------------------------
    if enforce_top and "TOP" not in sql_upper:
        return {
            "valid": False,
            "reason": "TOP clause missing. Row limit required."
        }

    # -----------------------------------
    # 6️⃣ Table whitelist check
    # -----------------------------------
    tables_used = extract_table_names(statement)

    for table in tables_used:
        clean_table = table.replace("[", "").replace("]", "")
        if clean_table.lower() not in [t.lower() for t in allowed_tables]:
            return {
                "valid": False,
                "reason": f"Unauthorized table detected: {clean_table}"
            }

    return {
        "valid": True,
        "reason": "SQL validated successfully."
    }