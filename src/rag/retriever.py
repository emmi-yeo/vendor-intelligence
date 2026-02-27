from src.rag.embedder import embed_texts


def retrieve_relevant_chunks(vector_store, query: str, top_k=5):
    query_embedding = embed_texts([query])[0]
    results = vector_store.search(query_embedding, top_k=top_k)
    return results