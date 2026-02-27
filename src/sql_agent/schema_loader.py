import os
import json
import pymssql
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()


# ============================
# 🔐 DATABASE CONNECTION
# ============================

def get_connection():
    return pymssql.connect(
        server=os.getenv("AZURE_SQL_SERVER"),
        user=os.getenv("AZURE_SQL_USERNAME"),
        password=os.getenv("AZURE_SQL_PASSWORD"),
        database=os.getenv("AZURE_SQL_DATABASE"),
        port=1433
    )


# ============================
# 📦 MAIN SCHEMA LOADER
# ============================

def load_schema_from_db() -> Dict:
    """
    Extract full schema metadata from Azure SQL.
    Returns structured dictionary.
    """
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)

    schema = {
        "database": os.getenv("AZURE_SQL_DATABASE"),
        "tables": []
    }

    # ----------------------------
    # 1️⃣ GET TABLES
    # ----------------------------
    cursor.execute("""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        AND TABLE_SCHEMA = 'dbo'
    """)
    tables = cursor.fetchall()

    for table in tables:
        table_name = table["TABLE_NAME"]

        table_info = {
            "name": table_name,
            "columns": [],
            "primary_keys": [],
            "foreign_keys": [],
            "indexes": []
        }

        # ----------------------------
        # 2️⃣ GET COLUMNS
        # ----------------------------
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = '{table_name}'
        """)
        columns = cursor.fetchall()

        for col in columns:
            table_info["columns"].append({
                "name": col["COLUMN_NAME"],
                "type": col["DATA_TYPE"],
                "nullable": col["IS_NULLABLE"] == "YES"
            })

        # ----------------------------
        # 3️⃣ PRIMARY KEYS
        # ----------------------------
        cursor.execute(f"""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_NAME = '{table_name}'
            AND OBJECTPROPERTY(
                OBJECT_ID(CONSTRAINT_NAME),
                'IsPrimaryKey'
            ) = 1
        """)
        pks = cursor.fetchall()
        table_info["primary_keys"] = [pk["COLUMN_NAME"] for pk in pks]

        # ----------------------------
        # 4️⃣ FOREIGN KEYS
        # ----------------------------
        cursor.execute(f"""
            SELECT
                fk.name AS fk_name,
                parent_col.name AS parent_column,
                ref_tab.name AS referenced_table,
                ref_col.name AS referenced_column
            FROM sys.foreign_keys fk
            INNER JOIN sys.foreign_key_columns fkc
                ON fkc.constraint_object_id = fk.object_id
            INNER JOIN sys.tables parent_tab
                ON parent_tab.object_id = fk.parent_object_id
            INNER JOIN sys.columns parent_col
                ON parent_col.column_id = fkc.parent_column_id
                AND parent_col.object_id = parent_tab.object_id
            INNER JOIN sys.tables ref_tab
                ON ref_tab.object_id = fk.referenced_object_id
            INNER JOIN sys.columns ref_col
                ON ref_col.column_id = fkc.referenced_column_id
                AND ref_col.object_id = ref_tab.object_id
            WHERE parent_tab.name = '{table_name}'
        """)
        fks = cursor.fetchall()

        for fk in fks:
            table_info["foreign_keys"].append({
                "fk_name": fk["fk_name"],
                "column": fk["parent_column"],
                "references_table": fk["referenced_table"],
                "references_column": fk["referenced_column"]
            })

        # ----------------------------
        # 5️⃣ INDEXES
        # ----------------------------
        cursor.execute(f"""
            SELECT i.name AS index_name, col.name AS column_name
            FROM sys.indexes i
            INNER JOIN sys.index_columns ic
                ON i.object_id = ic.object_id
                AND i.index_id = ic.index_id
            INNER JOIN sys.columns col
                ON ic.object_id = col.object_id
                AND ic.column_id = col.column_id
            INNER JOIN sys.tables t
                ON t.object_id = i.object_id
            WHERE t.name = '{table_name}'
        """)
        indexes = cursor.fetchall()

        for idx in indexes:
            table_info["indexes"].append({
                "index_name": idx["index_name"],
                "column": idx["column_name"]
            })

        schema["tables"].append(table_info)

    conn.close()
    return schema


# ============================
# 💾 CACHE HANDLING
# ============================

def save_schema_cache(schema: Dict, path: str = "data/schema_cache.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)


def load_schema_cache(path: str = "data/schema_cache.json") -> Dict:
    if not os.path.exists(path):
        raise FileNotFoundError("Schema cache not found. Run load_schema_from_db() first.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================
# 🤖 LLM-FRIENDLY SUMMARY
# ============================

def get_schema_summary_for_llm(schema: Dict) -> str:
    """
    Compress schema into readable summary for LLM context.
    Avoids sending full metadata.
    """
    summary_lines = []

    for table in schema["tables"]:
        cols = ", ".join([c["name"] for c in table["columns"]])
        summary_lines.append(f"Table: {table['name']} | Columns: {cols}")

    return "\n".join(summary_lines)


# ============================
# 🚀 RUN DIRECTLY (OPTIONAL)
# ============================

if __name__ == "__main__":
    print("Loading schema from Azure SQL...")
    schema_data = load_schema_from_db()
    save_schema_cache(schema_data)
    print("Schema saved to data/schema_cache.json")