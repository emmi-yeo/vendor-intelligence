import streamlit as st
import pandas as pd
from src.planner.hybrid_agent import run_hybrid_agent

st.set_page_config(
    page_title="Vendor Intelligence Agent POC",
    layout="wide"
)

st.title("🧠 Vendor Intelligence Agent (Hybrid SQL + RAG)")
st.caption("Planner-Based | Schema-Aware | Secure SQL | Requirement Matching")


# =====================================
# SIDEBAR
# =====================================

st.sidebar.header("Controls")

show_plan = st.sidebar.checkbox("Show Hybrid Plan", value=True)
show_sql = st.sidebar.checkbox("Show SQL Query", value=True)
show_rag = st.sidebar.checkbox("Show RAG Chunks", value=True)
show_scoring = st.sidebar.checkbox("Show Scoring", value=True)


# =====================================
# INPUT SECTION
# =====================================

user_query = st.text_input(
    "Enter your vendor search query:",
    placeholder="Example: Find construction vendors in Selangor with CIDB"
)

uploaded_file = st.file_uploader(
    "Upload requirement document (optional)",
    type=["pdf", "txt"]
)

run_button = st.button("Run Hybrid Agent")


# =====================================
# EXECUTION
# =====================================

if run_button and user_query:

    with st.spinner("Running Hybrid Intelligence Engine..."):

        result = run_hybrid_agent(
            user_query=user_query,
            uploaded_file=uploaded_file
        )

    st.success("Execution Completed")

    hybrid_plan = result.get("hybrid_plan")
    sql_result = result.get("sql_result")
    rag_result = result.get("rag_result")
    scored_result = result.get("scored_result")

    # =====================================
    # TABS
    # =====================================

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Results",
        "🧠 Plan",
        "📄 SQL",
        "📚 RAG"
    ])

    # -------------------------------------
    # TAB 1 - RESULTS
    # -------------------------------------

    with tab1:

        if scored_result:
            st.subheader("🏆 Ranked Vendors")
            st.dataframe(scored_result["ranked_dataframe"])
        elif sql_result and sql_result.get("dataframe") is not None:
            st.subheader("SQL Results")
            st.dataframe(sql_result["dataframe"])
        elif rag_result:
            st.subheader("RAG Output")
            st.write(rag_result)
        else:
            st.warning("No results returned.")

    # -------------------------------------
    # TAB 2 - PLAN
    # -------------------------------------

    with tab2:
        if show_plan and hybrid_plan:
            st.json(hybrid_plan)

    # -------------------------------------
    # TAB 3 - SQL
    # -------------------------------------

    with tab3:

        if sql_result:

            if sql_result.get("success"):

                if show_sql:
                    st.subheader("Generated SQL")
                    st.code(sql_result.get("sql"), language="sql")

                st.write("Row Count:", sql_result.get("row_count"))
                st.write("Execution Time (sec):", sql_result.get("execution_time_sec"))

            else:
                st.error("SQL Stage Failed")
                st.json(sql_result)

    # -------------------------------------
    # TAB 4 - RAG
    # -------------------------------------

    with tab4:

        if rag_result and show_rag:
            st.subheader("Retrieved Requirement Chunks")
            for i, chunk in enumerate(rag_result.get("retrieved_chunks", [])):
                st.markdown(f"**Chunk {i+1}**")
                st.write(chunk)