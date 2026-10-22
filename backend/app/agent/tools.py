from app.ingestion.storage import vector_store
from app.ingestion.embedder import embedder
from app.database.models import SessionLocal, Document

def search_documents(query: str, top_k: int = 5) -> str:
    query_embedding = embedder.embed_text(query)
    results = vector_store.search(query_embedding, top_k=top_k)
    
    if not results:
        return "No relevant documents found."
        
    output = "Found the following relevant information:\n\n"
    for i, r in enumerate(results, 1):
        output += f"[Source {i}] {r['metadata'].get('filename')} (Page {r['metadata'].get('page_number')}):\n"
        output += f"{r['text']}\n\n"
        
    return output


def list_documents() -> str:
    db = SessionLocal()
    try:
        docs = db.query(Document).all()
        if not docs:
            return "No documents in the knowledge base." 
        output = "Available documents:\n"
        for doc in docs:
            output += f"- {doc.filename} (ID: {doc.document_id})\n"
        return output
    finally:
        db.close()


def summarize_document(document_id: str) -> str:
    chunks = vector_store.get_document_chunks(document_id)
    
    if not chunks:
        return f"Document {document_id} not found or has no chunks."
        
    full_text = "\n".join([c["text"] for c in chunks])
    
    truncated_text = full_text[:4000]
    
    return f"Document content (truncated):\n{truncated_text}"