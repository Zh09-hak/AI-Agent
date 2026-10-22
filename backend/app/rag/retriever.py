from backend.app.ingestion.embedder import embedder
from backend.app.ingestion.storage import vector_store


def retrieve_relevant_chunks(
    query: str,
    top_k: int = 5,
) -> list[dict]:

    query_embedding = embedder.embed_text(query)
    results = vector_store.search(query_embedding, top_k=top_k)
    return results