from backend.app.rag.retriever import retrieve_relevant_chunks
from backend.app.rag.prompt_builder import build_rag_prompt
from backend.app.rag.llm_service import llm_service


def rag_query(
    history: list[dict],
    current_query: str,
    top_k: int = 5,
) -> dict:
    print(f"\n{'='*60}")
    print(f"Original Query: {current_query}")
    print(f"{'='*60}")
    
    print("\n[0/3] Rewriting query for better retrieval...")
    standalone_query = llm_service.rewrite_query(history, current_query)
    print(f"✓ Standalone query: '{standalone_query}'")
    
    print("\n[1/3] Retrieving relevant chunks...")
    chunks = retrieve_relevant_chunks(standalone_query, top_k=top_k)
    print(f"✓ Retrieved {len(chunks)} chunk(s)")
    
    print("\n[2/3] Building prompt...")
    prompt = build_rag_prompt(standalone_query, chunks) 
    print(f"✓ Prompt built ({len(prompt)} characters)")
    
    print("\n[3/3] Generating answer with LLM...")
    answer = llm_service.generate(prompt, temperature=0.1, max_tokens=2000)
    print(f"✓ Answer generated ({len(answer)} characters)")

    no_answer_phrases = [
        "i don't have enough information",
        "i do not have enough information",
        "cannot answer",
        "not enough information",
        "недостаточно информации",
        "нет информации"
    ]
    found_relevant_info = not any(phrase in answer.lower() for phrase in no_answer_phrases)
    sources = []
    if found_relevant_info:
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
        "found_relevant_info": found_relevant_info,
    }