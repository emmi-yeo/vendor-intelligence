import numpy as np
from typing import Dict, List
from src.rag.embedder import embed_texts


def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (
        np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-8
    )


def build_vendor_text_representation(df):
    """
    Convert vendor dataframe row into text blob
    for similarity comparison.
    """
    vendor_texts = []

    for _, row in df.iterrows():
        text_parts = []
        for col in df.columns:
            text_parts.append(f"{col}: {row[col]}")
        vendor_texts.append(" | ".join(text_parts))

    return vendor_texts


def score_vendors_against_requirements(
    sql_dataframe,
    rag_result
) -> Dict:

    if sql_dataframe is None or rag_result is None:
        return None

    requirement_text = " ".join(rag_result["retrieved_chunks"])

    # Embed requirement once
    requirement_embedding = embed_texts([requirement_text])[0]

    # Build vendor text
    vendor_texts = build_vendor_text_representation(sql_dataframe)

    vendor_embeddings = embed_texts(vendor_texts)

    scores = []

    for i, emb in enumerate(vendor_embeddings):
        score = cosine_similarity(emb, requirement_embedding)
        scores.append(score)

    sql_dataframe = sql_dataframe.copy()
    sql_dataframe["match_score"] = scores

    ranked_df = sql_dataframe.sort_values(
        by="match_score",
        ascending=False
    )

    return {
        "ranked_dataframe": ranked_df,
        "requirement_text_used": requirement_text
    }