from src.rag.file_processor import process_uploaded_file
from src.rag.embedder import embed_texts
from src.rag.vector_store import FAISSVectorStore
from src.rag.retriever import retrieve_relevant_chunks


def run_rag_pipeline(uploaded_file, user_query=None):

    # 1️⃣ Process file
    chunks = process_uploaded_file(uploaded_file)

    # 2️⃣ Embed chunks
    embeddings = embed_texts(chunks)

    # 3️⃣ Build vector store
    dimension = len(embeddings[0])
    store = FAISSVectorStore(dimension)
    store.add_embeddings(embeddings, chunks)

    # 4️⃣ Retrieve relevant chunks
    if user_query:
        relevant_chunks = retrieve_relevant_chunks(store, user_query)
    else:
        # If no query, just return top chunks
        relevant_chunks = chunks[:5]

    return {
        "total_chunks": len(chunks),
        "retrieved_chunks": relevant_chunks
    }