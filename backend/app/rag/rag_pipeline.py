from backend.app.rag.retriever import retrieve_relevant_chunks
from backend.app.rag.prompt_builder import build_rag_prompt
from backend.app.rag.llm_service import llm_service


def rag_query(
    question: str,
    top_k: int = 5,
) -> dict:
    print(f"\n{'='*60}")
    print(f"RAG Query: {question}")
    print(f"{'='*60}")
    
    print("\n[1/3] Retrieving relevant chunks...")
    chunks = retrieve_relevant_chunks(question, top_k=top_k)
    print(f"✓ Retrieved {len(chunks)} chunk(s)")
    
    print("\n[2/3] Building prompt...")
    prompt = build_rag_prompt(question, chunks)
    print(f"✓ Prompt built ({len(prompt)} characters)")
    
    print("\n[3/3] Generating answer with LLM...")
    answer = llm_service.generate(prompt, temperature=0.1)
    print(f"✓ Answer generated ({len(answer)} characters)")
    
    sources = []
    for i, chunk in enumerate(chunks, 1):
        metadata = chunk["metadata"]
        sources.append({
            "source_number": i,
            "filename": metadata.get("filename", "unknown"),
            "page_number": metadata.get("page_number"),
            "chunk_index": metadata.get("chunk_index", 0),
            "text": chunk["text"],
            "distance": chunk.get("distance"),
        })
    
    return {
        "answer": answer,
        "sources": sources,
        "retrieved_chunks": len(chunks),
    }